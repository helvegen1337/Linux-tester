# Linux Training Platform - Makefile
# Удобные команды для управления проектом

.PHONY: help install install-dev test clean run lint format setup-dev

# По умолчанию показываем help
help:
	@echo "🐧 Linux Training Platform - Команды управления"
	@echo ""
	@echo "📦 Установка:"
	@echo "  install       - Установка через pip"
	@echo "  install-dev   - Установка для разработки"
	@echo "  setup-dev     - Настройка окружения разработки"
	@echo ""
	@echo "🚀 Запуск:"
	@echo "  run           - Запуск тренажера"
	@echo "  test          - Запуск тестов"
	@echo ""
	@echo "🔧 Разработка:"
	@echo "  lint          - Проверка кода"
	@echo "  format        - Форматирование кода"
	@echo "  clean         - Очистка временных файлов"
	@echo ""
	@echo "📊 Информация:"
	@echo "  info          - Информация о проекте"

# Установка проекта
install:
	pip install .

# Установка для разработки
install-dev:
	pip install -e .[dev]

# Настройка окружения разработки
setup-dev:
	@echo "🔧 Настройка окружения разработки..."
	python -m pip install --upgrade pip
	pip install -e .[dev]
	@echo "✅ Окружение готово!"

# Запуск тренажера
run:
	python artix_training.py

# Запуск тестов (если есть)
test:
	@if [ -f "test_training.py" ]; then \
		python -m pytest test_training.py -v; \
	else \
		echo "⚠️  Тесты не найдены. Запускаем проверку JSON..."; \
		python -c "import json; json.load(open('training_data.json')); print('✅ JSON корректен')"; \
	fi

# Проверка кода
lint:
	@echo "🔍 Проверка Python кода..."
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 artix_training.py --max-line-length=120 --ignore=E501,W503; \
	else \
		echo "⚠️  flake8 не установлен"; \
	fi
	@echo "🔍 Проверка JSON файлов..."
	@python -c "import json; json.load(open('training_data.json')); print('✅ training_data.json корректен')"

# Форматирование кода
format:
	@echo "🎨 Форматирование кода..."
	@if command -v black >/dev/null 2>&1; then \
		black artix_training.py --line-length=120; \
	else \
		echo "⚠️  black не установлен. Установите: pip install black"; \
	fi

# Очистка временных файлов
clean:
	@echo "🧹 Очистка временных файлов..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.tmp" -delete
	find . -type f -name "*.bak" -delete
	find . -type f -name "training_log.txt" -delete 2>/dev/null || true
	rm -rf build/ dist/ *.egg-info/ 2>/dev/null || true
	@echo "✅ Очистка завершена"

# Информация о проекте
info:
	@echo "📊 Информация о проекте:"
	@echo "├── Название: Linux Training Platform"
	@echo "├── Язык: Python $(shell python --version 2>&1 | cut -d' ' -f2)"
	@echo "├── Размер основного скрипта: $(shell wc -l < artix_training.py) строк"
	@echo "├── Размер данных: $(shell wc -l < training_data.json) строк"
	@echo "├── Git статус: $(shell git status --porcelain | wc -l) изменений"
	@echo "└── Последний коммит: $(shell git log -1 --pretty=format:'%h - %s (%an, %ar)' 2>/dev/null || echo 'Нет git репозитория')"

# Создание дистрибутива
dist: clean
	@echo "📦 Создание дистрибутива..."
	python setup.py sdist bdist_wheel
	@echo "✅ Дистрибутив создан в dist/"

# Загрузка на PyPI (только для мейнтейнеров)
upload-test:
	@echo "🚀 Загрузка на Test PyPI..."
	python -m twine upload --repository testpypi dist/*

upload:
	@echo "🚀 Загрузка на PyPI..."
	python -m twine upload dist/*

# Создание GitHub release
release:
	@echo "🏷️  Создание GitHub release..."
	@echo "Убедитесь что:"
	@echo "1. Все изменения закоммичены"
	@echo "2. Версия обновлена в setup.py"
	@echo "3. Создан git tag с версией"
	@echo ""
	@echo "Для создания release выполните:"
	@echo "git tag v1.0.0 && git push origin v1.0.0"