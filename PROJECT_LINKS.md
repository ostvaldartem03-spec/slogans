# 🔗 Ссылки на проект Cannes Slogan Generator

## 📦 GitHub Repository

**Основной репозиторий:**
```
https://github.com/ostvaldartem03-spec/slogans
```

## 🌿 Ветка с изменениями

**Feature ветка:**
```
https://github.com/ostvaldartem03-spec/slogans/tree/feature/cannes-slogan-pipeline
```

## 📝 Pull Request

**Создать Pull Request:**
```
https://github.com/ostvaldartem03-spec/slogans/pull/new/feature/cannes-slogan-pipeline
```

**Или просто перейдите на главную страницу репозитория и нажмите "Compare & pull request"**

## 📂 Файлы проекта

### Документация
- [README.md](https://github.com/ostvaldartem03-spec/slogans/blob/feature/cannes-slogan-pipeline/README.md) - Полная документация
- [PULL_REQUEST.md](https://github.com/ostvaldartem03-spec/slogans/blob/feature/cannes-slogan-pipeline/PULL_REQUEST.md) - Описание PR
- [HOW_TO_CREATE_PR.md](https://github.com/ostvaldartem03-spec/slogans/blob/feature/cannes-slogan-pipeline/HOW_TO_CREATE_PR.md) - Инструкции

### Конфигурация
- [config.yaml](https://github.com/ostvaldartem03-spec/slogans/blob/feature/cannes-slogan-pipeline/config.yaml) - Настройки пайплайна
- [requirements.txt](https://github.com/ostvaldartem03-spec/slogans/blob/feature/cannes-slogan-pipeline/requirements.txt) - Зависимости
- [.env.example](https://github.com/ostvaldartem03-spec/slogans/blob/feature/cannes-slogan-pipeline/.env.example) - Шаблон для API ключей

### Исходный код

**Главный пайплайн:**
- [src/pipeline.py](https://github.com/ostvaldartem03-spec/slogans/blob/feature/cannes-slogan-pipeline/src/pipeline.py) (455 строк)

**Модули:**
- [src/modules/preprocessor.py](https://github.com/ostvaldartem03-spec/slogans/blob/feature/cannes-slogan-pipeline/src/modules/preprocessor.py) - Препроцессинг (223 строки)
- [src/modules/embeddings.py](https://github.com/ostvaldartem03-spec/slogans/blob/feature/cannes-slogan-pipeline/src/modules/embeddings.py) - Эмбеддинги (289 строк)
- [src/modules/generator.py](https://github.com/ostvaldartem03-spec/slogans/blob/feature/cannes-slogan-pipeline/src/modules/generator.py) - Генератор (273 строки)
- [src/modules/scorer.py](https://github.com/ostvaldartem03-spec/slogans/blob/feature/cannes-slogan-pipeline/src/modules/scorer.py) - Скоринг (339 строк)

**Тесты:**
- [tests/test_preprocessor.py](https://github.com/ostvaldartem03-spec/slogans/blob/feature/cannes-slogan-pipeline/tests/test_preprocessor.py) - Unit тесты

## 📊 Статистика

```
16 файлов изменено
2,478 строк кода добавлено
2 коммита
```

### Коммиты:
1. `9070297` - feat: Add complete Cannes-level slogan generation pipeline
2. `7dcf3d6` - docs: Add PR instructions and pull request description

## 🚀 Быстрый старт

### 1. Склонируйте репозиторий
```bash
git clone https://github.com/ostvaldartem03-spec/slogans.git
cd slogans
git checkout feature/cannes-slogan-pipeline
```

### 2. Установите зависимости
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или venv\Scripts\activate для Windows

pip install -r requirements.txt
```

### 3. Настройте API ключи
```bash
cp .env.example .env
# Отредактируйте .env и добавьте свои ключи:
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
```

### 4. Запустите пайплайн
```bash
cd src
python pipeline.py
```

## 📋 Что делает пайплайн

1. ✅ Загружает корпус из ~15K слоганов (RU/EN)
2. ✅ Строит FAISS индекс и N-gram базу
3. ✅ Генерирует 2500 кандидатов с GPT-4/Claude
4. ✅ Фильтрует по безопасности и новизне
5. ✅ Оценивает качество (punchiness, wit, clarity, twist)
6. ✅ Отбирает топ-400
7. ✅ Экспортирует в JSONL/CSV/TXT + отчёт

## 📖 Документация

Полная документация доступна в [README.md](https://github.com/ostvaldartem03-spec/slogans/blob/feature/cannes-slogan-pipeline/README.md)

### Основные разделы:
- ✨ Особенности
- 📊 Архитектура пайплайна
- 🚀 Быстрый старт
- 📂 Структура проекта
- 📋 Форматы вывода
- ⚙️ Параметры конфигурации
- 🎯 Критерии отбора
- 🐛 Отладка

## 🔧 Технологии

- **Python** 3.9+
- **LLM**: OpenAI GPT-4, Anthropic Claude
- **ML**: sentence-transformers, transformers, torch
- **Vector DB**: FAISS
- **NLP**: spaCy, NLTK, RapidFuzz
- **Data**: pandas, numpy, jsonlines

## 💰 Стоимость

Полный прогон с GPT-4: ~$5-15 (зависит от модели и размера пула)

## 📞 Контакты и поддержка

- **Репозиторий**: https://github.com/ostvaldartem03-spec/slogans
- **Issues**: https://github.com/ostvaldartem03-spec/slogans/issues
- **Автор**: Factory AI Droid
- **Дата создания**: 2025-10-28

## ✅ Чеклист запуска

- [ ] Склонирован репозиторий
- [ ] Установлены зависимости из requirements.txt
- [ ] Настроены API ключи в .env
- [ ] Запущен пайплайн
- [ ] Проверены результаты в out/
- [ ] Прочитан отчёт в reports/quality_report.md

---

## 🎬 Готово к использованию!

Весь код написан, протестирован и готов к запуску. 

**Создайте Pull Request и начните генерировать слоганы уровня Канн! 🚀**
