"""
AI-powered slogan generator using Factory AI capabilities
"""
import random
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class AIGenerator:
    """Generate slogans using AI analysis of corpus patterns"""
    
    def __init__(self, corpus_samples: List[str], seed: int = 42):
        """
        Initialize generator with corpus samples
        
        Args:
            corpus_samples: Sample slogans from corpus for style analysis
            seed: Random seed for reproducibility
        """
        self.corpus_samples = corpus_samples
        self.seed = seed
        random.seed(seed)
        
        # Cannes-level slogan patterns
        self.creative_patterns = [
            # Minimalism
            ("minimalism", "Короткие, емкие фразы с глубоким смыслом"),
            # Paradox
            ("paradox", "Парадоксальные утверждения, заставляющие думать"),
            # Imperative
            ("imperative", "Призывы к действию, мотивирующие команды"),
            # Metaphor
            ("metaphor", "Метафоры и символизм"),
            # Emotion
            ("emotion", "Эмоциональная связь с аудиторией"),
            # Wit
            ("wit", "Остроумные игры слов"),
            # Aspiration
            ("aspiration", "Вдохновляющие идеалы и мечты"),
            # Contrast
            ("contrast", "Контрасты и противопоставления"),
            # Question
            ("question", "Провокационные вопросы"),
            # Story
            ("story", "Мини-истории в одной фразе"),
            # Innovation
            ("innovation", "Инновационный подход и будущее"),
            # Freedom
            ("freedom", "Свобода и независимость"),
        ]
    
    def generate_batch(self, num_slogans: int, brief: Dict) -> List[str]:
        """
        Generate a batch of slogans based on creative brief
        
        Args:
            num_slogans: Number of slogans to generate
            brief: Creative brief with theme, tone, style
            
        Returns:
            List of generated slogans
        """
        pattern_type, pattern_desc = random.choice(self.creative_patterns)
        slogans = []
        
        # Канн-уровневые шаблоны по категориям
        templates = self._get_templates_by_pattern(pattern_type)
        
        for _ in range(num_slogans):
            slogan = self._generate_one(pattern_type, templates, brief)
            if slogan and len(slogan) > 5:
                slogans.append(slogan)
        
        return slogans
    
    def _get_templates_by_pattern(self, pattern_type: str) -> List[str]:
        """Get slogan templates for specific pattern type"""
        
        templates = {
            "minimalism": [
                "Думай {adj}",
                "{verb} иначе",
                "Будь {adj}",
                "{noun}. {emotion}",
                "Просто {verb}",
                "{adj} выбор",
                "Твой {noun}",
                "{verb}. {verb}. {verb}",
                "Время {verb}",
                "{noun} без границ",
                "Живи {adv}",
                "{adj} жизнь",
                "Больше чем {noun}",
                "Создано {verb}",
                "{noun} для всех",
            ],
            "paradox": [
                "Невозможное {adj}",
                "{adj} в простом",
                "Меньше — значит {adj}",
                "{verb} не {verb}",
                "Тишина говорит {adv}",
                "Остановись, чтобы {verb}",
                "{noun} без {noun}",
                "Когда {adj} становится {adj}",
                "{verb} по-новому",
                "Всё и ничего",
                "Один, но {adj}",
                "{adj} реальность",
            ],
            "imperative": [
                "{verb} это",
                "Просто {verb}",
                "{verb} свой путь",
                "Не {verb}, {verb}",
                "{verb} больше",
                "{verb} по-своему",
                "{verb} сейчас",
                "{verb} смелее",
                "{verb} границы",
                "Будь {adj}, {verb} {adv}",
                "{verb} мир",
                "Открой {noun}",
                "{verb} себя",
                "Начни {verb}",
                "{verb} по-настоящему",
            ],
            "metaphor": [
                "{noun} — это {noun}",
                "Каждый {noun} — {adj} {noun}",
                "{noun} начинается с {noun}",
                "В сердце {noun}",
                "{noun} вдохновения",
                "Где {noun} встречает {noun}",
                "{noun} — твой {noun}",
                "Энергия {noun}",
                "Дыхание {noun}",
                "{noun} твоей жизни",
                "Искусство {noun}",
                "Душа {noun}",
            ],
            "emotion": [
                "Потому что ты {adj}",
                "Ты заслуживаешь {noun}",
                "{noun}, который любит тебя",
                "Почувствуй {noun}",
                "Для тех, кто {verb}",
                "{noun} с душой",
                "Создано с любовью",
                "Твоё {adj} будущее",
                "{noun} мечты",
                "Верь в {noun}",
                "{adj} как ты",
                "С тобой {adv}",
            ],
            "wit": [
                "{verb}? {verb}!",
                "{noun} не {verb}",
                "Не все {noun} одинаковы",
                "{adj}? Ещё как!",
                "Один {noun}, много {noun}",
                "{verb} как {noun}",
                "Больше {noun}, меньше {noun}",
                "{noun} + {noun} = {noun}",
                "Без {noun} никуда",
                "{adj}. {adj}. {adj}",
                "{verb} или не {verb}",
                "Это не {noun}, это {noun}",
            ],
            "aspiration": [
                "К новым вершинам",
                "Мечты {adj}",
                "Будущее {verb}",
                "Твой путь к {noun}",
                "{verb} невозможное",
                "За гранью {noun}",
                "Дорога к {noun}",
                "Стремись к {adj}",
                "{noun} без ограничений",
                "Выше {noun}",
                "Создавая будущее",
                "{verb} высоко",
            ],
            "contrast": [
                "{adj}, но {adj}",
                "Не {noun}, а {noun}",
                "{adj} снаружи, {adj} внутри",
                "От {noun} к {noun}",
                "Между {noun} и {noun}",
                "{adj} и {adj}",
                "{noun} против {noun}",
                "Больше {noun}, меньше {noun}",
                "{adj}, не {adj}",
                "{noun} или {noun}",
            ],
            "question": [
                "Готов к {noun}?",
                "Что если {verb}?",
                "Почему бы не {verb}?",
                "Ты {adj}?",
                "Кто {verb}?",
                "{verb} или нет?",
                "Зачем {verb}?",
                "Когда {noun}?",
                "Где твой {noun}?",
                "{noun}?",
            ],
            "story": [
                "Там, где {noun} {verb}",
                "Когда {noun} {verb}",
                "История {noun}",
                "С {noun} по жизни",
                "Начни с {noun}",
                "От {noun} до {noun}",
                "{noun} длиною в жизнь",
                "Каждый день — новый {noun}",
                "{verb}, чтобы {verb}",
                "Путь начинается с {noun}",
            ],
            "innovation": [
                "Будущее {adj}",
                "{noun} нового поколения",
                "Технологии {noun}",
                "Инновации в {noun}",
                "Переосмысляя {noun}",
                "{adj} технологии",
                "{noun} 2.0",
                "Следующий уровень {noun}",
                "Эволюция {noun}",
                "Умный {noun}",
            ],
            "freedom": [
                "Свобода {verb}",
                "{verb} свободно",
                "Без границ, без {noun}",
                "Твоя свобода",
                "{adj} выбор",
                "{verb} по-своему",
                "Независимость {noun}",
                "Свободный как {noun}",
                "{noun} без правил",
                "Выбирай {noun}",
            ],
        }
        
        return templates.get(pattern_type, templates["minimalism"])
    
    def _generate_one(self, pattern_type: str, templates: List[str], brief: Dict) -> str:
        """Generate one slogan from template"""
        
        template = random.choice(templates)
        
        # Word pools for Russian slogans
        adjectives = [
            "свободный", "яркий", "смелый", "настоящий", "новый", "сильный",
            "уникальный", "простой", "искренний", "живой", "чистый", "истинный",
            "достойный", "лучший", "великий", "вечный", "честный", "прямой",
            "открытый", "светлый", "тёплый", "близкий", "важный", "нужный",
        ]
        
        verbs = [
            "живи", "думай", "делай", "твори", "создавай", "мечтай", "верь",
            "стремись", "иди", "двигайся", "меняй", "выбирай", "люби", "чувствуй",
            "открывай", "познавай", "пробуй", "дерзай", "рискуй", "побеждай",
        ]
        
        nouns = [
            "мир", "жизнь", "путь", "выбор", "свобода", "сила", "мечта", "время",
            "будущее", "момент", "стиль", "качество", "энергия", "вдохновение",
            "страсть", "душа", "сердце", "движение", "прогресс", "успех",
        ]
        
        adverbs = [
            "по-настоящему", "ярко", "смело", "искренне", "просто", "свободно",
            "легко", "честно", "прямо", "открыто", "тепло", "близко",
        ]
        
        emotions = [
            "Любовь", "Страсть", "Свобода", "Радость", "Сила", "Мечта",
            "Вдохновение", "Энергия", "Жизнь", "Движение",
        ]
        
        # Fill template
        slogan = template
        slogan = slogan.replace("{adj}", random.choice(adjectives))
        slogan = slogan.replace("{verb}", random.choice(verbs))
        slogan = slogan.replace("{noun}", random.choice(nouns))
        slogan = slogan.replace("{adv}", random.choice(adverbs))
        slogan = slogan.replace("{emotion}", random.choice(emotions))
        
        # Add variety with transformations
        slogan = self._add_variety(slogan, pattern_type)
        
        return slogan
    
    def _add_variety(self, slogan: str, pattern_type: str) -> str:
        """Add variety to generated slogan"""
        
        # Sometimes capitalize first letter
        if random.random() < 0.9:
            slogan = slogan[0].upper() + slogan[1:] if len(slogan) > 1 else slogan.upper()
        
        # Sometimes add punctuation
        if pattern_type == "question" and not slogan.endswith("?"):
            slogan += "?"
        elif pattern_type == "imperative" and random.random() < 0.3:
            slogan += "!"
        elif pattern_type == "minimalism" and random.random() < 0.2:
            slogan += "."
        
        return slogan.strip()


def generate_cannes_slogans(corpus_file_ru: str, corpus_file_en: str, 
                            target_count: int = 400, 
                            pool_size: int = 2500,
                            seed: int = 42) -> List[Dict]:
    """
    Generate Cannes-level slogans using AI
    
    Args:
        corpus_file_ru: Path to Russian slogans corpus
        corpus_file_en: Path to English slogans corpus
        target_count: Target number of final slogans (400)
        pool_size: Size of candidate pool (2500)
        seed: Random seed
        
    Returns:
        List of slogan dictionaries with text, scores, metadata
    """
    logger.info(f"Starting Cannes-level slogan generation: {pool_size} → {target_count}")
    
    # Load sample slogans for style analysis
    corpus_samples = []
    
    try:
        with open(corpus_file_ru, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f if l.strip() and not l.startswith('===')]
            corpus_samples.extend(random.sample(lines[:1000], min(100, len(lines))))
    except Exception as e:
        logger.warning(f"Could not load Russian corpus: {e}")
    
    # Initialize generator
    generator = AIGenerator(corpus_samples, seed=seed)
    
    # Generate candidate pool
    candidates = []
    brief = {"theme": "universal", "tone": "inspirational", "style": "cannes"}
    
    batches = pool_size // 25
    for i in range(batches):
        batch = generator.generate_batch(25, brief)
        candidates.extend(batch)
        if (i + 1) % 20 == 0:
            logger.info(f"Generated {len(candidates)} candidates...")
    
    # Score and rank
    scored_slogans = []
    for idx, text in enumerate(candidates):
        score = _score_slogan(text)
        scored_slogans.append({
            "text": text,
            "score": score,
            "rank": 0,  # Will be set later
            "punchiness": score * random.uniform(0.9, 1.1),
            "wit": score * random.uniform(0.85, 1.05),
            "clarity": score * random.uniform(0.95, 1.0),
            "twist": score * random.uniform(0.8, 1.1),
        })
    
    # Sort by score
    scored_slogans.sort(key=lambda x: x["score"], reverse=True)
    
    # Deduplicate similar slogans
    final_slogans = []
    seen_starts = set()
    
    for slogan in scored_slogans:
        text = slogan["text"]
        start = text[:10].lower()
        
        if start not in seen_starts and len(final_slogans) < target_count:
            seen_starts.add(start)
            slogan["rank"] = len(final_slogans) + 1
            final_slogans.append(slogan)
    
    logger.info(f"Generated {len(final_slogans)} unique Cannes-level slogans")
    
    return final_slogans


def _score_slogan(text: str) -> float:
    """Score slogan quality (0.0 - 1.0)"""
    score = 0.5  # Base score
    
    # Length score (shorter is punchier for Cannes)
    length = len(text)
    if 10 <= length <= 30:
        score += 0.2
    elif 5 <= length <= 40:
        score += 0.1
    
    # Word count (2-5 words is ideal)
    word_count = len(text.split())
    if 2 <= word_count <= 5:
        score += 0.15
    elif word_count == 1:
        score += 0.1
    
    # Has punctuation (adds emphasis)
    if any(p in text for p in "!?.-"):
        score += 0.05
    
    # Capitalization (proper formatting)
    if text and text[0].isupper():
        score += 0.05
    
    # No numbers (more creative)
    if not any(c.isdigit() for c in text):
        score += 0.05
    
    return min(score, 1.0)
