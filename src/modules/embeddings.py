"""
Embeddings and vector similarity module
"""
import os
import pickle
from typing import List, Tuple, Optional
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from tqdm import tqdm


class EmbeddingIndex:
    """Handles embedding generation and similarity search"""
    
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
                 cache_dir: str = ".cache"):
        """
        Initialize embedding model and index
        
        Args:
            model_name: Sentence transformer model name
            cache_dir: Directory to cache embeddings and index
        """
        self.model_name = model_name
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        
        self.index: Optional[faiss.Index] = None
        self.slogans: List[str] = []
        self.embeddings: Optional[np.ndarray] = None
        
    def encode_batch(self, texts: List[str], batch_size: int = 32,
                     show_progress: bool = True) -> np.ndarray:
        """
        Encode texts to embeddings
        
        Args:
            texts: List of text strings
            batch_size: Batch size for encoding
            show_progress: Show progress bar
            
        Returns:
            numpy array of embeddings (n_texts x dimension)
        """
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True,
            normalize_embeddings=True  # L2 normalization for cosine similarity
        )
        return embeddings
    
    def build_index(self, slogans: List[str], batch_size: int = 64) -> None:
        """
        Build FAISS index from slogans
        
        Args:
            slogans: List of slogan strings
            batch_size: Batch size for encoding
        """
        print(f"Building embedding index for {len(slogans)} slogans...")
        
        self.slogans = slogans
        
        # Encode all slogans
        self.embeddings = self.encode_batch(slogans, batch_size=batch_size)
        
        # Create FAISS index (Inner Product for normalized vectors = cosine similarity)
        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(self.embeddings)
        
        print(f"Index built with {self.index.ntotal} vectors")
    
    def search(self, query: str, k: int = 5) -> List[Tuple[str, float, int]]:
        """
        Search for k most similar slogans
        
        Args:
            query: Query text
            k: Number of results to return
            
        Returns:
            List of (slogan, similarity_score, index) tuples
        """
        if self.index is None:
            raise ValueError("Index not built. Call build_index() first.")
        
        # Encode query
        query_embedding = self.encode_batch([query], batch_size=1, show_progress=False)
        
        # Search
        similarities, indices = self.index.search(query_embedding, k)
        
        # Return results
        results = []
        for idx, sim in zip(indices[0], similarities[0]):
            if idx < len(self.slogans):
                results.append((self.slogans[idx], float(sim), int(idx)))
        
        return results
    
    def get_nearest_neighbor(self, text: str) -> Tuple[str, float, int]:
        """
        Get single nearest neighbor
        
        Args:
            text: Query text
            
        Returns:
            Tuple of (nearest_slogan, similarity, index)
        """
        results = self.search(text, k=1)
        return results[0] if results else ("", 0.0, -1)
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute cosine similarity between two texts
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Cosine similarity score (0-1)
        """
        embeddings = self.encode_batch([text1, text2], show_progress=False)
        
        # Cosine similarity (already normalized)
        similarity = float(np.dot(embeddings[0], embeddings[1]))
        return similarity
    
    def batch_check_novelty(self, candidates: List[str], 
                           threshold: float = 0.80) -> List[Tuple[str, bool, float]]:
        """
        Check novelty of candidate slogans against corpus
        
        Args:
            candidates: List of candidate slogans
            threshold: Maximum similarity threshold (below = novel)
            
        Returns:
            List of (slogan, is_novel, max_similarity) tuples
        """
        if self.index is None:
            raise ValueError("Index not built. Call build_index() first.")
        
        print(f"Checking novelty for {len(candidates)} candidates...")
        
        # Encode all candidates
        candidate_embeddings = self.encode_batch(candidates, batch_size=64)
        
        # Search for nearest neighbors
        similarities, _ = self.index.search(candidate_embeddings, 1)
        
        results = []
        for slogan, sim_array in zip(candidates, similarities):
            max_sim = float(sim_array[0])
            is_novel = max_sim < threshold
            results.append((slogan, is_novel, max_sim))
        
        novel_count = sum(1 for _, is_novel, _ in results if is_novel)
        print(f"Novel candidates: {novel_count}/{len(candidates)} "
              f"({100*novel_count/len(candidates):.1f}%)")
        
        return results
    
    def save(self, path: str) -> None:
        """Save index and metadata to disk"""
        print(f"Saving index to {path}")
        
        # Save FAISS index
        faiss.write_index(self.index, f"{path}.faiss")
        
        # Save metadata
        metadata = {
            'model_name': self.model_name,
            'slogans': self.slogans,
            'embeddings': self.embeddings,
            'dimension': self.dimension
        }
        with open(f"{path}.pkl", 'wb') as f:
            pickle.dump(metadata, f)
        
        print(f"Index saved successfully")
    
    def load(self, path: str) -> None:
        """Load index and metadata from disk"""
        print(f"Loading index from {path}")
        
        # Load FAISS index
        self.index = faiss.read_index(f"{path}.faiss")
        
        # Load metadata
        with open(f"{path}.pkl", 'rb') as f:
            metadata = pickle.load(f)
        
        self.slogans = metadata['slogans']
        self.embeddings = metadata['embeddings']
        self.dimension = metadata['dimension']
        
        # Verify model matches
        if metadata['model_name'] != self.model_name:
            print(f"Warning: Loaded index was built with {metadata['model_name']}, "
                  f"but current model is {self.model_name}")
        
        print(f"Index loaded with {self.index.ntotal} vectors")


class NGramChecker:
    """Check for n-gram overlap between texts"""
    
    def __init__(self, n: int = 5):
        """
        Initialize n-gram checker
        
        Args:
            n: Size of n-grams
        """
        self.n = n
        self.corpus_ngrams = set()
    
    def extract_ngrams(self, text: str) -> set:
        """Extract n-grams from text"""
        tokens = text.lower().split()
        ngrams = set()
        
        for i in range(len(tokens) - self.n + 1):
            ngram = tuple(tokens[i:i + self.n])
            ngrams.add(ngram)
        
        return ngrams
    
    def build_corpus_ngrams(self, slogans: List[str]) -> None:
        """Build set of all n-grams in corpus"""
        print(f"Building {self.n}-gram index for {len(slogans)} slogans...")
        
        for slogan in tqdm(slogans, desc="Extracting n-grams"):
            self.corpus_ngrams.update(self.extract_ngrams(slogan))
        
        print(f"Indexed {len(self.corpus_ngrams)} unique {self.n}-grams")
    
    def check_overlap(self, text: str) -> Tuple[bool, float, set]:
        """
        Check if text has n-gram overlap with corpus
        
        Args:
            text: Text to check
            
        Returns:
            Tuple of (has_overlap, overlap_ratio, overlapping_ngrams)
        """
        text_ngrams = self.extract_ngrams(text)
        
        if not text_ngrams:
            return False, 0.0, set()
        
        overlapping = text_ngrams & self.corpus_ngrams
        overlap_ratio = len(overlapping) / len(text_ngrams)
        has_overlap = len(overlapping) > 0
        
        return has_overlap, overlap_ratio, overlapping
    
    def batch_check(self, texts: List[str]) -> List[Tuple[str, bool, float]]:
        """
        Check multiple texts for n-gram overlap
        
        Args:
            texts: List of texts to check
            
        Returns:
            List of (text, has_overlap, max_overlap_ratio) tuples
        """
        results = []
        
        for text in tqdm(texts, desc=f"Checking {self.n}-gram overlap"):
            has_overlap, overlap_ratio, _ = self.check_overlap(text)
            results.append((text, has_overlap, overlap_ratio))
        
        clean_count = sum(1 for _, has_overlap, _ in results if not has_overlap)
        print(f"Clean candidates: {clean_count}/{len(texts)} "
              f"({100*clean_count/len(texts):.1f}%)")
        
        return results
