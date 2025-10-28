"""
Main pipeline for Cannes-level slogan generation
"""
import os
import json
import uuid
import yaml
from datetime import datetime
from typing import List, Dict
import jsonlines
import pandas as pd
from dotenv import load_dotenv

from modules.preprocessor import SloganPreprocessor
from modules.embeddings import EmbeddingIndex, NGramChecker
from modules.generator import SloganGenerator
from modules.scorer import SafetyFilter, StyleScorer


class CannesSloganPipeline:
    """Complete pipeline for generating Cannes-level slogans"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize pipeline with configuration"""
        load_dotenv()
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # Extract config
        self.language = self.config['pipeline']['target_language']
        self.seed = self.config['pipeline']['seed']
        self.target_count = self.config['pipeline']['target_count']
        self.candidate_pool_size = self.config['pipeline']['candidate_pool_size']
        
        # Create output directories
        for dir_key in ['output_dir', 'reports_dir', 'logs_dir', 'cache_dir']:
            os.makedirs(self.config['data'][dir_key], exist_ok=True)
        
        # Initialize components
        self.preprocessor = SloganPreprocessor()
        self.embedding_index = None
        self.ngram_checker = None
        self.generator = None
        self.safety_filter = None
        self.scorer = None
        
        # Stats
        self.stats = {
            'start_time': datetime.now().isoformat(),
            'corpus_size': 0,
            'candidates_generated': 0,
            'filters': {},
            'final_count': 0
        }
    
    def load_corpus(self) -> List[str]:
        """Load and preprocess corpus"""
        print("=" * 60)
        print("STEP 1: Loading and preprocessing corpus")
        print("=" * 60)
        
        # Select corpus file based on language
        if self.language == 'ru':
            corpus_file = self.config['data']['russian_corpus']
        else:
            corpus_file = self.config['data']['english_corpus']
        
        # Process corpus
        slogans, corpus_stats = self.preprocessor.process_corpus(corpus_file)
        
        self.stats['corpus_size'] = len(slogans)
        self.stats['corpus_stats'] = corpus_stats
        
        return slogans
    
    def build_indices(self, corpus: List[str]) -> None:
        """Build embedding and n-gram indices"""
        print("\n" + "=" * 60)
        print("STEP 2: Building embedding and n-gram indices")
        print("=" * 60)
        
        # Embedding index
        model_name = self.config['embeddings']['model_name']
        cache_dir = self.config['data']['cache_dir']
        
        self.embedding_index = EmbeddingIndex(
            model_name=model_name,
            cache_dir=cache_dir
        )
        
        index_path = os.path.join(cache_dir, f"corpus_index_{self.language}")
        
        # Try to load existing index
        if os.path.exists(f"{index_path}.faiss"):
            print("Loading existing index...")
            self.embedding_index.load(index_path)
        else:
            print("Building new index...")
            self.embedding_index.build_index(corpus)
            self.embedding_index.save(index_path)
        
        # N-gram checker
        self.ngram_checker = NGramChecker(n=self.config['novelty']['ngram_size'])
        self.ngram_checker.build_corpus_ngrams(corpus)
    
    def generate_candidates(self) -> List[str]:
        """Generate candidate slogans"""
        print("\n" + "=" * 60)
        print("STEP 3: Generating candidate slogans")
        print("=" * 60)
        
        self.generator = SloganGenerator(
            model=self.config['generation']['model'],
            language=self.language,
            provider="openai"
        )
        
        candidates = self.generator.generate_candidates(
            target_count=self.candidate_pool_size,
            batch_size=self.config['pipeline']['batch_size'],
            temperature=self.config['generation']['temperature'],
            top_p=self.config['generation']['top_p'],
            presence_penalty=self.config['generation']['presence_penalty'],
            seed=self.seed
        )
        
        self.stats['candidates_generated'] = len(candidates)
        
        # Save raw candidates
        raw_path = os.path.join(self.config['data']['cache_dir'], 'raw_candidates.txt')
        with open(raw_path, 'w', encoding='utf-8') as f:
            for c in candidates:
                f.write(f"{c}\n")
        
        return candidates
    
    def filter_safety(self, candidates: List[str]) -> List[str]:
        """Filter unsafe content"""
        print("\n" + "=" * 60)
        print("STEP 4: Safety filtering")
        print("=" * 60)
        
        self.safety_filter = SafetyFilter(
            language=self.language,
            use_llm=self.config['safety']['check_toxicity']
        )
        
        results = self.safety_filter.batch_filter(candidates)
        
        safe = [text for text, is_safe, _ in results if is_safe]
        rejected = [(text, reason) for text, is_safe, reason in results if not is_safe]
        
        self.stats['filters']['safety'] = {
            'input': len(candidates),
            'output': len(safe),
            'rejected': len(rejected)
        }
        
        return safe
    
    def check_corpus_novelty(self, candidates: List[str]) -> List[str]:
        """Check novelty against corpus"""
        print("\n" + "=" * 60)
        print("STEP 5: Checking novelty against corpus")
        print("=" * 60)
        
        threshold = self.config['novelty']['embedding_similarity_threshold']
        
        # Embedding similarity check
        novelty_results = self.embedding_index.batch_check_novelty(
            candidates, threshold=threshold
        )
        
        novel_embedding = [slogan for slogan, is_novel, _ in novelty_results if is_novel]
        
        print(f"\nPassed embedding check: {len(novel_embedding)}/{len(candidates)}")
        
        # N-gram overlap check
        ngram_results = self.ngram_checker.batch_check(novel_embedding)
        
        novel_final = [text for text, has_overlap, _ in ngram_results if not has_overlap]
        
        self.stats['filters']['novelty'] = {
            'input': len(candidates),
            'after_embedding': len(novel_embedding),
            'after_ngram': len(novel_final),
            'rejected': len(candidates) - len(novel_final)
        }
        
        return novel_final
    
    def internal_deduplication(self, candidates: List[str]) -> List[str]:
        """Remove duplicates within candidates"""
        print("\n" + "=" * 60)
        print("STEP 6: Internal deduplication")
        print("=" * 60)
        
        # Exact dedup
        candidates = self.preprocessor.deduplicate_exact(candidates)
        
        # Fuzzy dedup
        threshold = self.config['novelty']['internal_dedup_threshold']
        candidates = self.preprocessor.deduplicate_fuzzy(
            candidates, 
            threshold=threshold * 100  # Convert to percentage
        )
        
        self.stats['filters']['internal_dedup'] = {
            'output': len(candidates)
        }
        
        return candidates
    
    def score_and_filter(self, candidates: List[str]) -> List[Dict]:
        """Score quality and filter by thresholds"""
        print("\n" + "=" * 60)
        print("STEP 7: Quality scoring and filtering")
        print("=" * 60)
        
        self.scorer = StyleScorer(language=self.language, use_llm=False)
        
        # Score all candidates (using fast heuristics)
        scored = self.scorer.batch_score(candidates, use_llm=False)
        
        # Filter by thresholds
        quality_config = self.config['quality']
        filtered = self.scorer.filter_by_thresholds(
            scored,
            min_punchiness=quality_config['min_punchiness'],
            min_wit=quality_config['min_wit'],
            min_clarity=quality_config['min_clarity'],
            min_twist=quality_config['min_twist']
        )
        
        # Rank by weighted score
        ranked = self.scorer.rank_by_score(
            filtered,
            weights=self.config['weights']
        )
        
        self.stats['filters']['quality'] = {
            'input': len(candidates),
            'output': len(ranked),
            'rejected': len(candidates) - len(ranked)
        }
        
        # Convert to structured format
        results = []
        for text, scores, total_score in ranked:
            # Get novelty info
            _, _, max_sim = self.embedding_index.get_nearest_neighbor(text)
            
            results.append({
                'text': text,
                'scores': scores,
                'total_score': total_score,
                'novelty_sim': max_sim,
                'word_count': len(text.split())
            })
        
        return results
    
    def select_top_n(self, scored_results: List[Dict], n: int = 400) -> List[Dict]:
        """Select top N slogans with balancing"""
        print("\n" + "=" * 60)
        print(f"STEP 8: Selecting top {n} slogans")
        print("=" * 60)
        
        # Sort by total score
        scored_results.sort(key=lambda x: x['total_score'], reverse=True)
        
        # Select top N
        selected = scored_results[:n]
        
        print(f"Selected {len(selected)} slogans")
        
        # Analyze distribution
        word_counts = [s['word_count'] for s in selected]
        avg_words = sum(word_counts) / len(word_counts)
        
        print(f"Word count distribution: avg={avg_words:.1f}, "
              f"min={min(word_counts)}, max={max(word_counts)}")
        
        self.stats['final_count'] = len(selected)
        self.stats['avg_word_count'] = avg_words
        
        return selected
    
    def export_results(self, results: List[Dict]) -> None:
        """Export results in multiple formats"""
        print("\n" + "=" * 60)
        print("STEP 9: Exporting results")
        print("=" * 60)
        
        output_dir = self.config['data']['output_dir']
        
        # Add IDs and format
        final_results = []
        for i, r in enumerate(results):
            final_results.append({
                'id': str(uuid.uuid4()),
                'text': r['text'],
                'lang': self.language,
                'len_words': r['word_count'],
                'novelty': {
                    'embed_sim_to_nn': round(r['novelty_sim'], 3)
                },
                'style': {
                    'punchiness': round(r['scores']['punchiness'], 2),
                    'wit': round(r['scores']['wit'], 2),
                    'twist': round(r['scores']['twist'], 2),
                    'clarity': round(r['scores']['clarity'], 2)
                },
                'devices': r['scores'].get('devices', []),
                'flags': [],
                'total_score': round(r['total_score'], 3)
            })
        
        # JSONL
        jsonl_path = os.path.join(output_dir, 'cannes_400.jsonl')
        with jsonlines.open(jsonl_path, 'w') as writer:
            writer.write_all(final_results)
        print(f"Saved: {jsonl_path}")
        
        # CSV
        csv_path = os.path.join(output_dir, 'cannes_400.csv')
        df = pd.DataFrame([
            {
                'id': r['id'],
                'text': r['text'],
                'lang': r['lang'],
                'len_words': r['len_words'],
                'embed_sim': r['novelty']['embed_sim_to_nn'],
                'punchiness': r['style']['punchiness'],
                'wit': r['style']['wit'],
                'clarity': r['style']['clarity'],
                'twist': r['style']['twist'],
                'total_score': r['total_score']
            }
            for r in final_results
        ])
        df.to_csv(csv_path, index=False, encoding='utf-8')
        print(f"Saved: {csv_path}")
        
        # TXT
        txt_path = os.path.join(output_dir, 'cannes_400.txt')
        with open(txt_path, 'w', encoding='utf-8') as f:
            for r in final_results:
                f.write(f"{r['text']}\n")
        print(f"Saved: {txt_path}")
    
    def generate_report(self) -> None:
        """Generate quality report"""
        print("\n" + "=" * 60)
        print("STEP 10: Generating report")
        print("=" * 60)
        
        report_path = os.path.join(
            self.config['data']['reports_dir'],
            'quality_report.md'
        )
        
        self.stats['end_time'] = datetime.now().isoformat()
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# Cannes-Level Slogan Generation Report\n\n")
            f.write(f"**Generated:** {self.stats['end_time']}\n\n")
            f.write(f"**Language:** {self.language}\n\n")
            
            f.write("## Pipeline Configuration\n\n")
            f.write(f"- Target count: {self.target_count}\n")
            f.write(f"- Candidate pool size: {self.candidate_pool_size}\n")
            f.write(f"- Random seed: {self.seed}\n")
            f.write(f"- LLM model: {self.config['generation']['model']}\n\n")
            
            f.write("## Corpus Statistics\n\n")
            f.write(f"- Total slogans: {self.stats['corpus_size']}\n")
            stats = self.stats['corpus_stats']
            f.write(f"- Avg word count: {stats['word_count']['mean']:.1f}\n")
            f.write(f"- Unique words: {stats['unique_words']}\n\n")
            
            f.write("## Pipeline Results\n\n")
            f.write(f"1. Candidates generated: {self.stats['candidates_generated']}\n")
            
            for step, data in self.stats['filters'].items():
                f.write(f"2. After {step}: {data['output']} ")
                if 'rejected' in data:
                    f.write(f"({data['rejected']} rejected)")
                f.write("\n")
            
            f.write(f"\n**Final output:** {self.stats['final_count']} slogans\n\n")
            
            f.write("## Quality Metrics\n\n")
            f.write(f"- Average word count: {self.stats['avg_word_count']:.1f}\n")
            f.write(f"- Embedding similarity threshold: {self.config['novelty']['embedding_similarity_threshold']}\n")
            f.write(f"- N-gram size: {self.config['novelty']['ngram_size']}\n\n")
            
            f.write("## Output Files\n\n")
            f.write("- `out/cannes_400.jsonl` - Full structured data\n")
            f.write("- `out/cannes_400.csv` - Tabular format\n")
            f.write("- `out/cannes_400.txt` - Plain text slogans\n")
        
        print(f"Report saved: {report_path}")
        
        # Save logs
        logs_path = os.path.join(self.config['data']['logs_dir'], 'run.json')
        with open(logs_path, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)
        print(f"Logs saved: {logs_path}")
    
    def run(self) -> None:
        """Run complete pipeline"""
        print("\n" + "🎬" * 30)
        print("CANNES-LEVEL SLOGAN GENERATION PIPELINE")
        print("🎬" * 30 + "\n")
        
        # 1. Load corpus
        corpus = self.load_corpus()
        
        # 2. Build indices
        self.build_indices(corpus)
        
        # 3. Generate candidates
        candidates = self.generate_candidates()
        
        # 4. Safety filter
        candidates = self.filter_safety(candidates)
        
        # 5. Novelty check
        candidates = self.check_corpus_novelty(candidates)
        
        # 6. Internal dedup
        candidates = self.internal_deduplication(candidates)
        
        # 7. Score and filter
        scored = self.score_and_filter(candidates)
        
        # 8. Select top N
        final = self.select_top_n(scored, n=self.target_count)
        
        # 9. Export
        self.export_results(final)
        
        # 10. Report
        self.generate_report()
        
        print("\n" + "✅" * 30)
        print("PIPELINE COMPLETE!")
        print("✅" * 30 + "\n")


if __name__ == "__main__":
    pipeline = CannesSloganPipeline("config.yaml")
    pipeline.run()
