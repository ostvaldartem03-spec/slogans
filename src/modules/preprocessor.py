"""
Preprocessing and deduplication module for slogan corpus
"""
import re
import hashlib
from typing import List, Set, Tuple
from collections import Counter
import numpy as np
from rapidfuzz import fuzz


class SloganPreprocessor:
    """Handles corpus preprocessing and deduplication"""
    
    def __init__(self):
        self.seen_hashes: Set[str] = set()
        self.processed_slogans: List[str] = []
        
    def normalize_text(self, text: str) -> str:
        """Normalize whitespace, quotes, and punctuation"""
        # Remove HTML entities
        text = re.sub(r'&[a-z]+;', ' ', text)
        text = re.sub(r'&#\d+;', ' ', text)
        
        # Normalize quotes
        text = text.replace('«', '"').replace('»', '"')
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace("'", "'").replace("'", "'")
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def is_valid_slogan(self, text: str) -> bool:
        """Check if text is a valid slogan"""
        if not text or len(text) < 5:
            return False
            
        # Skip metadata lines
        if any(marker in text.lower() for marker in [
            'бренд:', 'brand:', 'слоган:', 'slogan:', 
            'дата', 'date', 'всего', 'total', '===',
            '[база', '[slogans'
        ]):
            return False
            
        # Skip lines that are just numbers
        if re.match(r'^\d+\.?\s*$', text):
            return False
            
        # Must contain at least one letter
        if not re.search(r'[a-zа-яё]', text, re.IGNORECASE):
            return False
            
        return True
    
    def extract_slogan(self, line: str) -> str:
        """Extract clean slogan from formatted line"""
        # Remove numbering at start
        line = re.sub(r'^\d+\.\s*', '', line)
        
        # Split by common separators and take first part
        # (often metadata follows)
        for sep in ['&emsp;', '  ', '\t']:
            if sep in line:
                parts = line.split(sep)
                line = parts[0]
                break
        
        return self.normalize_text(line)
    
    def compute_hash(self, text: str) -> str:
        """Compute hash for exact deduplication"""
        normalized = text.lower().strip()
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def compute_simhash(self, text: str, num_bits: int = 64) -> int:
        """Compute SimHash for near-duplicate detection"""
        tokens = text.lower().split()
        
        # Create feature vector
        v = [0] * num_bits
        for token in tokens:
            h = int(hashlib.md5(token.encode()).hexdigest(), 16)
            for i in range(num_bits):
                if h & (1 << i):
                    v[i] += 1
                else:
                    v[i] -= 1
        
        # Convert to fingerprint
        fingerprint = 0
        for i in range(num_bits):
            if v[i] > 0:
                fingerprint |= (1 << i)
        
        return fingerprint
    
    def hamming_distance(self, hash1: int, hash2: int) -> int:
        """Calculate Hamming distance between two hashes"""
        x = hash1 ^ hash2
        distance = 0
        while x:
            distance += 1
            x &= x - 1
        return distance
    
    def load_and_clean_corpus(self, filepath: str) -> List[str]:
        """Load corpus and perform initial cleaning"""
        slogans = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                extracted = self.extract_slogan(line)
                
                if self.is_valid_slogan(extracted):
                    slogans.append(extracted)
        
        print(f"Loaded {len(slogans)} raw slogans from {filepath}")
        return slogans
    
    def deduplicate_exact(self, slogans: List[str]) -> List[str]:
        """Remove exact duplicates using hash"""
        unique = []
        seen = set()
        
        for slogan in slogans:
            h = self.compute_hash(slogan)
            if h not in seen:
                seen.add(h)
                unique.append(slogan)
        
        print(f"Exact deduplication: {len(slogans)} -> {len(unique)} "
              f"({len(slogans) - len(unique)} removed)")
        return unique
    
    def deduplicate_fuzzy(self, slogans: List[str], 
                          threshold: float = 92.0) -> List[str]:
        """Remove near-duplicates using SimHash and fuzzy matching"""
        if not slogans:
            return []
        
        # Sort by length (keep longer versions)
        slogans_with_len = [(s, len(s)) for s in slogans]
        slogans_with_len.sort(key=lambda x: x[1], reverse=True)
        
        unique = []
        simhashes = []
        
        for slogan, _ in slogans_with_len:
            is_duplicate = False
            current_hash = self.compute_simhash(slogan)
            
            # Check against existing unique slogans
            for i, existing in enumerate(unique):
                # SimHash check (fast)
                if self.hamming_distance(current_hash, simhashes[i]) < 5:
                    # Fuzzy string match (slower, more accurate)
                    similarity = fuzz.ratio(slogan.lower(), existing.lower())
                    if similarity >= threshold:
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                unique.append(slogan)
                simhashes.append(current_hash)
        
        print(f"Fuzzy deduplication: {len(slogans)} -> {len(unique)} "
              f"({len(slogans) - len(unique)} removed)")
        return unique
    
    def analyze_corpus(self, slogans: List[str]) -> dict:
        """Analyze corpus statistics"""
        word_counts = [len(s.split()) for s in slogans]
        char_counts = [len(s) for s in slogans]
        
        all_words = []
        for s in slogans:
            all_words.extend(s.lower().split())
        
        word_freq = Counter(all_words)
        
        return {
            'total_slogans': len(slogans),
            'word_count': {
                'min': min(word_counts),
                'max': max(word_counts),
                'mean': np.mean(word_counts),
                'median': np.median(word_counts)
            },
            'char_count': {
                'min': min(char_counts),
                'max': max(char_counts),
                'mean': np.mean(char_counts),
                'median': np.median(char_counts)
            },
            'unique_words': len(word_freq),
            'most_common_words': word_freq.most_common(20)
        }
    
    def process_corpus(self, filepath: str) -> Tuple[List[str], dict]:
        """Full preprocessing pipeline"""
        # Load and clean
        slogans = self.load_and_clean_corpus(filepath)
        
        # Deduplicate
        slogans = self.deduplicate_exact(slogans)
        slogans = self.deduplicate_fuzzy(slogans)
        
        # Analyze
        stats = self.analyze_corpus(slogans)
        
        print(f"\nFinal corpus: {stats['total_slogans']} unique slogans")
        print(f"Word count: {stats['word_count']['mean']:.1f} avg "
              f"(min={stats['word_count']['min']}, max={stats['word_count']['max']})")
        
        return slogans, stats
