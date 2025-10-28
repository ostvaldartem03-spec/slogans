# 📝 Как создать Pull Request

## Текущий статус

✅ Весь код написан и закоммичен в ветку `feature/cannes-slogan-pipeline`  
✅ Все файлы готовы к PR  
⚠️ Требуется ручной push с вашими GitHub credentials

## Шаги для создания PR

### 1. Убедитесь, что вы в правильной ветке

```bash
cd /project/workspace/slogans
git branch
# Должно показать: * feature/cannes-slogan-pipeline
```

### 2. Настройте GitHub аутентификацию

Есть несколько вариантов:

#### Вариант A: Personal Access Token (рекомендуется)

```bash
# Создайте Personal Access Token на GitHub:
# Settings → Developer settings → Personal access tokens → Generate new token
# Выберите scope: repo

# Затем используйте:
git push https://<YOUR_TOKEN>@github.com/ostvaldartem03-spec/slogans.git feature/cannes-slogan-pipeline
```

#### Вариант B: SSH

```bash
# Если у вас настроен SSH ключ
git remote set-url origin git@github.com:ostvaldartem03-spec/slogans.git
git push -u origin feature/cannes-slogan-pipeline
```

#### Вариант C: GitHub CLI

```bash
gh auth login
git push -u origin feature/cannes-slogan-pipeline
```

### 3. Создайте Pull Request на GitHub

После успешного push:

1. Перейдите на https://github.com/ostvaldartem03-spec/slogans
2. Вы увидите кнопку **"Compare & pull request"** для вашей ветки
3. Нажмите её
4. Заголовок PR (уже заполнен): `feat: Add complete Cannes-level slogan generation pipeline`
5. В описание скопируйте содержимое файла `PULL_REQUEST.md`
6. Нажмите **"Create pull request"**

## Что включено в PR

### Новые файлы (14)
```
.env.example          - Шаблон для API ключей
.gitignore           - Git ignore rules
README.md            - Полная документация
config.yaml          - Конфигурация пайплайна
requirements.txt     - Python зависимости

src/
├── __init__.py
├── pipeline.py      - Главный пайплайн
└── modules/
    ├── __init__.py
    ├── preprocessor.py    - Очистка и дедупликация
    ├── embeddings.py      - Векторный поиск
    ├── generator.py       - LLM генерация
    └── scorer.py          - Качество и безопасность

tests/
├── __init__.py
└── test_preprocessor.py   - Unit тесты
```

### Коммит
```
commit 9070297
feat: Add complete Cannes-level slogan generation pipeline

- Implemented full 10-step reproducible pipeline for generating 400 Cannes-quality slogans
- Added corpus preprocessing with exact and fuzzy deduplication
- Integrated FAISS-based embedding similarity search for novelty checking
- Implemented 5-gram overlap detection against corpus
- Created LLM-based slogan generator with 12 creative briefs
- Added safety filtering (regex + optional LLM)
- Implemented heuristic quality scoring (punchiness, wit, clarity, twist)
- Added weighted ranking and top-N selection
- Export results in JSONL, CSV, and TXT formats
- Generate quality report with pipeline statistics
- Full configuration via YAML
- Supports both Russian and English generation
- Reproducible with seed-based generation
- Complete documentation in README
```

## Проверка перед push

```bash
# Проверьте статус
git status

# Проверьте коммиты
git log --oneline -5

# Проверьте изменения
git show HEAD --stat

# Должно показать:
# 14 files changed, 2082 insertions(+)
```

## Альтернатива: Ручное создание PR через Web UI

Если push не работает, можно создать PR вручную:

1. Создайте новую ветку через GitHub Web UI
2. Загрузите файлы через "Add file" → "Upload files"
3. Загрузите все файлы из списка выше
4. Создайте PR с main как base branch

## Тестирование после merge

После того как PR будет смержен в main:

```bash
git checkout main
git pull origin main

# Установите зависимости
pip install -r requirements.txt

# Настройте API ключи
cp .env.example .env
# Отредактируйте .env

# Запустите пайплайн
cd src
python pipeline.py
```

## Возможные проблемы

### "Permission denied"
- Проверьте, что у вас есть права на push в репозиторий
- Используйте Personal Access Token вместо пароля

### "Branch already exists"
- Если ветка уже существует на remote, используйте:
```bash
git push origin feature/cannes-slogan-pipeline --force
```

### "Authentication failed"
- Убедитесь, что токен/пароль правильный
- Для HTTPS используйте token, а не пароль

## Контакты

Если возникли вопросы:
- Проверьте `README.md` для документации
- Смотрите `PULL_REQUEST.md` для деталей изменений
- Все модули документированы с docstrings

---

**Удачи с PR! 🚀**
