"""
Quality scoring and safety filtering module
"""
import re
from typing import List, Dict, Tuple, Optional
import os
from openai import OpenAI


class SafetyFilter:
    """Filter unsafe, toxic, or problematic content"""
    
    # Patterns for quick regex filtering
    FORBIDDEN_PATTERNS_RU = [
        r'\b(гарантир|лечит|излечи|вылечи|100%|навсегда)\b',
        r'\b(лучш|идеальн|непревзойд|номер один|#1)\b',
        r'®|™|©',
        r'\b(конкурент|соперник)\b'
    ]
    
    FORBIDDEN_PATTERNS_EN = [
        r'\b(guarantee|cure|heal|100%|forever)\b',
        r'\b(best|perfect|unbeatable|number one|#1)\b',
        r'®|™|©',
        r'\b(competitor|rival)\b'
    ]
    
    FORBIDDEN_TOPICS = [
        "medical", "legal", "political", "discrimination",
        "violence", "sexual", "drugs", "weapons"
    ]
    
    def __init__(self, language: str = "ru", use_llm: bool = True):
        """
        Initialize safety filter
        
        Args:
            language: Target language
            use_llm: Use LLM for advanced safety checks
        """
        self.language = language
        self.use_llm = use_llm
        self.patterns = (self.FORBIDDEN_PATTERNS_RU if language == "ru" 
                        else self.FORBIDDEN_PATTERNS_EN)
        
        if use_llm:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def quick_check(self, text: str) -> Tuple[bool, str]:
        """
        Quick regex-based safety check
        
        Returns:
            (is_safe, reason)
        """
        for pattern in self.patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False, f"Forbidden pattern: {pattern}"
        
        return True, ""
    
    def llm_safety_check(self, text: str) -> Tuple[bool, str, float]:
        """
        LLM-based safety classification
        
        Returns:
            (is_safe, reason, confidence)
        """
        if not self.use_llm:
            return True, "", 1.0
        
        prompt = f"""Analyze this slogan for safety concerns:

Slogan: "{text}"

Check for:
- Toxicity, hate speech, discrimination
- Medical/health claims
- Legal guarantees or promises
- Political statements
- Violence or harm
- Inappropriate content

Respond with JSON:
{{"safe": true/false, "reason": "explanation", "confidence": 0.0-1.0}}"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=150
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return result["safe"], result.get("reason", ""), result.get("confidence", 0.0)
            
        except Exception as e:
            print(f"LLM safety check error: {e}")
            return True, "", 0.0
    
    def batch_filter(self, texts: List[str]) -> List[Tuple[str, bool, str]]:
        """
        Filter batch of texts
        
        Returns:
            List of (text, is_safe, reason) tuples
        """
        results = []
        
        for text in texts:
            # Quick check first
            is_safe, reason = self.quick_check(text)
            
            if not is_safe:
                results.append((text, False, reason))
                continue
            
            # LLM check for passed texts (optional, can be slow)
            # Uncomment for stricter filtering
            # is_safe, reason, conf = self.llm_safety_check(text)
            
            results.append((text, is_safe, reason))
        
        safe_count = sum(1 for _, is_safe, _ in results if is_safe)
        print(f"Safety filter: {safe_count}/{len(texts)} passed "
              f"({100*safe_count/len(texts):.1f}%)")
        
        return results


class StyleScorer:
    """Score slogan style quality (punchiness, wit, clarity, twist)"""
    
    def __init__(self, language: str = "ru", use_llm: bool = True):
        """
        Initialize scorer
        
        Args:
            language: Target language
            use_llm: Use LLM for quality scoring
        """
        self.language = language
        self.use_llm = use_llm
        
        if use_llm:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def heuristic_score(self, text: str) -> Dict[str, float]:
        """
        Fast heuristic scoring
        
        Returns:
            Dict with punchiness, wit, clarity, twist scores
        """
        words = text.split()
        word_count = len(words)
        
        # Punchiness: favor short, impactful
        if word_count <= 4:
            punchiness = 0.9
        elif word_count <= 6:
            punchiness = 0.7
        else:
            punchiness = 0.5
        
        # Clarity: penalize very long or very short
        if 3 <= word_count <= 7:
            clarity = 0.8
        else:
            clarity = 0.6
        
        # Wit: look for wordplay markers (rough heuristic)
        wit = 0.6
        if '?' in text or '!' in text:
            wit += 0.1
        
        # Twist: placeholder (hard to detect heuristically)
        twist = 0.6
        
        return {
            'punchiness': punchiness,
            'wit': wit,
            'clarity': clarity,
            'twist': twist
        }
    
    def llm_score(self, text: str) -> Dict[str, any]:
        """
        LLM-based quality scoring
        
        Returns:
            Dict with scores, devices, and explanation
        """
        if not self.use_llm:
            return self.heuristic_score(text)
        
        lang_note = "Russian" if self.language == "ru" else "English"
        
        prompt = f"""Rate this {lang_note} slogan on Cannes Lions creative quality:

Slogan: "{text}"

Score each dimension (0.0-1.0):

1. PUNCHINESS - Conciseness and impact. Short, powerful statements score higher.
2. WIT - Cleverness, wordplay, unexpected combinations, humor.
3. CLARITY - Easy to understand, clear message, no confusion.
4. TWIST - Semantic shift, surprise ending, "aha moment".

Also identify rhetorical DEVICES used (e.g., антитеза, аллитерация, метафора, парадокс).

Respond with JSON:
{{
  "punchiness": 0.0-1.0,
  "wit": 0.0-1.0,
  "clarity": 0.0-1.0,
  "twist": 0.0-1.0,
  "devices": ["device1", "device2"],
  "explanation": "brief analysis"
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=300
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            
            return {
                'punchiness': float(result.get('punchiness', 0.6)),
                'wit': float(result.get('wit', 0.6)),
                'clarity': float(result.get('clarity', 0.7)),
                'twist': float(result.get('twist', 0.5)),
                'devices': result.get('devices', []),
                'explanation': result.get('explanation', '')
            }
            
        except Exception as e:
            print(f"LLM scoring error for '{text}': {e}")
            return {**self.heuristic_score(text), 'devices': [], 'explanation': ''}
    
    def batch_score(self, texts: List[str], 
                   use_llm: bool = False) -> List[Tuple[str, Dict]]:
        """
        Score batch of texts
        
        Args:
            texts: List of slogans
            use_llm: Use expensive LLM scoring (vs fast heuristics)
            
        Returns:
            List of (text, scores_dict) tuples
        """
        results = []
        
        print(f"Scoring {len(texts)} slogans...")
        
        for i, text in enumerate(texts):
            if use_llm and self.use_llm:
                scores = self.llm_score(text)
            else:
                scores = self.heuristic_score(text)
                scores['devices'] = []
                scores['explanation'] = ''
            
            results.append((text, scores))
            
            if (i + 1) % 100 == 0:
                print(f"Scored {i + 1}/{len(texts)}")
        
        return results
    
    def filter_by_thresholds(self, scored_texts: List[Tuple[str, Dict]],
                            min_punchiness: float = 0.65,
                            min_wit: float = 0.60,
                            min_clarity: float = 0.70,
                            min_twist: float = 0.50) -> List[Tuple[str, Dict]]:
        """
        Filter scored texts by quality thresholds
        
        Returns:
            Filtered list of (text, scores) tuples
        """
        filtered = []
        
        for text, scores in scored_texts:
            if (scores['punchiness'] >= min_punchiness and
                scores['wit'] >= min_wit and
                scores['clarity'] >= min_clarity and
                scores['twist'] >= min_twist):
                filtered.append((text, scores))
        
        print(f"Quality filter: {len(filtered)}/{len(scored_texts)} passed "
              f"({100*len(filtered)/len(scored_texts):.1f}%)")
        
        return filtered
    
    def rank_by_score(self, scored_texts: List[Tuple[str, Dict]],
                     weights: Dict[str, float] = None) -> List[Tuple[str, Dict, float]]:
        """
        Rank scored texts by weighted score
        
        Args:
            scored_texts: List of (text, scores) tuples
            weights: Dict of dimension weights (default: equal)
            
        Returns:
            List of (text, scores, total_score) sorted by score descending
        """
        if weights is None:
            weights = {
                'punchiness': 0.30,
                'wit': 0.25,
                'clarity': 0.20,
                'twist': 0.15,
                'novelty': 0.10
            }
        
        ranked = []
        
        for text, scores in scored_texts:
            total = (
                scores['punchiness'] * weights.get('punchiness', 0.25) +
                scores['wit'] * weights.get('wit', 0.25) +
                scores['clarity'] * weights.get('clarity', 0.25) +
                scores['twist'] * weights.get('twist', 0.25)
            )
            ranked.append((text, scores, total))
        
        # Sort by total score descending
        ranked.sort(key=lambda x: x[2], reverse=True)
        
        return ranked
