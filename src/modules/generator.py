"""
Slogan generation module using LLM
"""
import os
import random
from typing import List, Optional
from openai import OpenAI
import anthropic


class SloganGenerator:
    """Generate creative slogans using LLM"""
    
    # Creative briefs for diverse generation
    CREATIVE_BRIEFS_RU = [
        "Минимализм: создай короткий, ударный слоган из 2-4 слов",
        "Парадокс: используй неожиданное сочетание или противоречие",
        "Повелительное: команда к действию, сильный глагол",
        "Антитеза: противопоставление двух идей",
        "Игра слов: используй омонимы, каламбур или двойной смысл",
        "Ритм: создай ритмичный слоган с аллитерацией",
        "Сдвиг смысла: начни с одного, закончи неожиданным поворотом",
        "Метафора: используй яркую метафору или образ",
        "Вопрос-ответ: построй слоган как вопрос или ответ",
        "Простота: обычные слова, глубокий смысл",
        "Контраст: сопоставь несопоставимое",
        "Эмоция: вызови сильное чувство одной фразой"
    ]
    
    CREATIVE_BRIEFS_EN = [
        "Minimalism: create a short, punchy 2-4 word slogan",
        "Paradox: use unexpected combination or contradiction",
        "Imperative: command to action, strong verb",
        "Antithesis: contrast two ideas",
        "Wordplay: use homonyms, puns or double meaning",
        "Rhythm: create rhythmic slogan with alliteration",
        "Twist: start with one thing, end with unexpected turn",
        "Metaphor: use vivid metaphor or image",
        "Question-answer: build as question or answer",
        "Simplicity: common words, deep meaning",
        "Contrast: juxtapose the incomparable",
        "Emotion: evoke strong feeling in one phrase"
    ]
    
    def __init__(self, api_key: Optional[str] = None, 
                 model: str = "gpt-4",
                 language: str = "ru",
                 provider: str = "openai"):
        """
        Initialize generator
        
        Args:
            api_key: API key (or from env)
            model: Model name
            language: Target language (ru/en)
            provider: LLM provider (openai/anthropic)
        """
        self.model = model
        self.language = language
        self.provider = provider
        
        if provider == "openai":
            self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        elif provider == "anthropic":
            self.client = anthropic.Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        else:
            raise ValueError(f"Unknown provider: {provider}")
        
        self.briefs = self.CREATIVE_BRIEFS_RU if language == "ru" else self.CREATIVE_BRIEFS_EN
    
    def build_system_prompt(self, language: str) -> str:
        """Build system prompt for slogan generation"""
        if language == "ru":
            return """Ты - креативный директор мирового уровня, специализирующийся на создании рекламных слоганов класса Cannes Lions.

ТВОЯ ЗАДАЧА: Генерировать оригинальные, запоминающиеся слоганы.

ОБЯЗАТЕЛЬНЫЕ ПРАВИЛА:
- Длина: 2-8 слов (оптимально 4-6)
- Тон: дерзкий, умный, с неожиданным поворотом
- Используй простые слова, но создавай глубокий смысл
- Высокая запоминаемость
- БЕЗ названий брендов
- БЕЗ знаков ®™©
- БЕЗ клише типа "лучший", "качество", "надежность"
- БЕЗ прямых отсылок к известным слоганам
- ИЗБЕГАЙ банальностей и штампов

ЗАПРЕЩЕНО:
- Медицинские обещания
- Сравнения с конкурентами
- Политические высказывания
- Дискриминация любого рода
- Токсичность

СТИЛЬ: Канны, D&AD, One Show - короткие фразы, которые врезаются в память."""
        else:
            return """You are a world-class creative director specializing in Cannes Lions-level advertising slogans.

YOUR TASK: Generate original, memorable slogans.

MANDATORY RULES:
- Length: 2-8 words (optimal 4-6)
- Tone: bold, witty, with unexpected twist
- Use simple words, create deep meaning
- High memorability
- NO brand names
- NO ®™© symbols
- NO clichés like "best", "quality", "reliable"
- NO direct references to famous slogans
- AVOID banalities and templates

FORBIDDEN:
- Medical claims
- Competitor comparisons
- Political statements
- Any discrimination
- Toxicity

STYLE: Cannes, D&AD, One Show - short phrases that stick in memory."""
    
    def build_generation_prompt(self, brief: str, count: int, language: str) -> str:
        """Build generation prompt with creative brief"""
        if language == "ru":
            return f"""Креативный бриф: {brief}

Создай {count} абсолютно ОРИГИНАЛЬНЫХ слоганов следуя этому брифу.

Каждый слоган должен:
- Быть уникальным и непохожим на существующие
- Вызывать "ага-эффект" или улыбку
- Работать как универсальный слоган (не для конкретного бренда)
- Быть лаконичным и ударным

Верни ТОЛЬКО слоганы, по одному на строку, без нумерации и комментариев."""
        else:
            return f"""Creative brief: {brief}

Create {count} absolutely ORIGINAL slogans following this brief.

Each slogan must:
- Be unique and unlike existing ones
- Create "aha moment" or smile
- Work as universal slogan (not for specific brand)
- Be concise and punchy

Return ONLY slogans, one per line, no numbering or comments."""
    
    def generate_batch_openai(self, prompt: str, system_prompt: str,
                             temperature: float = 0.9,
                             top_p: float = 0.95,
                             presence_penalty: float = 0.7) -> List[str]:
        """Generate batch using OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                top_p=top_p,
                presence_penalty=presence_penalty,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse slogans (one per line)
            slogans = []
            for line in content.split('\n'):
                line = line.strip()
                # Remove numbering
                line = line.lstrip('0123456789.-) ')
                if line and len(line) > 5:
                    slogans.append(line)
            
            return slogans
            
        except Exception as e:
            print(f"Error generating batch: {e}")
            return []
    
    def generate_batch_anthropic(self, prompt: str, system_prompt: str,
                                 temperature: float = 0.9,
                                 top_p: float = 0.95) -> List[str]:
        """Generate batch using Anthropic API"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=temperature,
                top_p=top_p,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response.content[0].text.strip()
            
            # Parse slogans
            slogans = []
            for line in content.split('\n'):
                line = line.strip()
                line = line.lstrip('0123456789.-) ')
                if line and len(line) > 5:
                    slogans.append(line)
            
            return slogans
            
        except Exception as e:
            print(f"Error generating batch: {e}")
            return []
    
    def generate_candidates(self, target_count: int = 2500,
                          batch_size: int = 25,
                          temperature: float = 0.9,
                          top_p: float = 0.95,
                          presence_penalty: float = 0.7,
                          seed: Optional[int] = None) -> List[str]:
        """
        Generate candidate pool of slogans
        
        Args:
            target_count: Target number of candidates
            batch_size: Slogans per API call
            temperature: LLM temperature
            top_p: LLM top_p
            presence_penalty: LLM presence penalty (OpenAI only)
            seed: Random seed for reproducibility
            
        Returns:
            List of candidate slogans
        """
        if seed is not None:
            random.seed(seed)
        
        system_prompt = self.build_system_prompt(self.language)
        candidates = []
        
        # Calculate number of batches needed
        num_batches = (target_count + batch_size - 1) // batch_size
        
        print(f"Generating {target_count} candidates in {num_batches} batches...")
        
        for i in range(num_batches):
            # Rotate through creative briefs
            brief = self.briefs[i % len(self.briefs)]
            
            prompt = self.build_generation_prompt(brief, batch_size, self.language)
            
            # Generate
            if self.provider == "openai":
                batch = self.generate_batch_openai(
                    prompt, system_prompt, temperature, top_p, presence_penalty
                )
            else:
                batch = self.generate_batch_anthropic(
                    prompt, system_prompt, temperature, top_p
                )
            
            candidates.extend(batch)
            
            print(f"Batch {i+1}/{num_batches}: Generated {len(batch)} slogans "
                  f"(total: {len(candidates)})")
            
            # Stop if we reached target
            if len(candidates) >= target_count:
                break
        
        print(f"\nGenerated {len(candidates)} total candidates")
        return candidates[:target_count]
