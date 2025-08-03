#!/bin/bash

# 🐧 Linux Training Platform - Установщик
# Автоматическая установка интерактивного тренажера Linux

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Конфигурация
REPO_URL="https://github.com/helvegen1337/linux-training-platform.git"
DEFAULT_INSTALL_DIR="$HOME/.local/share/linux-training"
SCRIPT_NAME="linux-training"

echo -e "${PURPLE}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║${NC} ${CYAN}🐧 Linux Interactive Training Platform${NC}       ${PURPLE}║${NC}"
echo -e "${PURPLE}║${NC} ${YELLOW}Установщик для Linux/macOS${NC}                   ${PURPLE}║${NC}"
echo -e "${PURPLE}╚══════════════════════════════════════════════════╝${NC}"
echo

# Функция для вывода ошибок
error() {
    echo -e "${RED}❌ Ошибка: $1${NC}" >&2
    exit 1
}

# Функция для вывода успеха
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Функция для вывода информации
info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Функция для вывода предупреждений
warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Проверка зависимостей
check_dependencies() {
    info "Проверка зависимостей..."
    
    # Проверка Python
    if ! command -v python3 &> /dev/null; then
        error "Python 3 не найден. Установите Python 3.6 или новее."
    fi
    
    # Проверка Git
    if ! command -v git &> /dev/null; then
        error "Git не найден. Установите Git для загрузки проекта."
    fi
    
    # Проверка версии Python
    python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    if ! python3 -c 'import sys; exit(0 if sys.version_info >= (3, 6) else 1)'; then
        error "Требуется Python 3.6 или новее. Найдена версия: $python_version"
    fi
    
    success "Все зависимости найдены (Python $python_version, Git)"
}

# Получение директории установки
get_install_dir() {
    echo -e "${CYAN}📁 Выберите директорию для установки:${NC}"
    echo -e "   Нажмите Enter для установки в: ${GREEN}$DEFAULT_INSTALL_DIR${NC}"
    echo -e "   Или введите свой путь:"
    
    read -r user_input
    
    if [ -z "$user_input" ]; then
        INSTALL_DIR="$DEFAULT_INSTALL_DIR"
    else
        # Расширяем ~ в полный путь
        INSTALL_DIR="${user_input/#\~/$HOME}"
    fi
    
    info "Директория установки: $INSTALL_DIR"
}

# Создание директории и клонирование
install_files() {
    info "Создание директории установки..."
    
    # Создаем директорию если её нет
    mkdir -p "$INSTALL_DIR" || error "Не удалось создать директорию: $INSTALL_DIR"
    
    # Клонируем репозиторий
    info "Загрузка проекта из GitHub..."
    if [ -d "$INSTALL_DIR/.git" ]; then
        warning "Директория уже содержит git репозиторий. Обновляем..."
        cd "$INSTALL_DIR"
        git pull origin main || error "Не удалось обновить репозиторий"
    else
        git clone "$REPO_URL" "$INSTALL_DIR" || error "Не удалось клонировать репозиторий"
    fi
    
    success "Проект успешно загружен"
}

# Создание запускаемого скрипта
create_launcher() {
    info "Создание launcher скрипта..."
    
    # Определяем директорию для исполняемых файлов
    if [ -d "$HOME/.local/bin" ]; then
        BIN_DIR="$HOME/.local/bin"
    elif [ -d "$HOME/bin" ]; then
        BIN_DIR="$HOME/bin"
    else
        BIN_DIR="$HOME/.local/bin"
        mkdir -p "$BIN_DIR"
    fi
    
    # Создаем launcher скрипт
    cat > "$BIN_DIR/$SCRIPT_NAME" << EOF
#!/bin/bash
# Linux Training Platform Launcher
cd "$INSTALL_DIR"
python3 artix_training.py "\$@"
EOF
    
    # Делаем скрипт исполняемым
    chmod +x "$BIN_DIR/$SCRIPT_NAME"
    
    success "Launcher создан: $BIN_DIR/$SCRIPT_NAME"
    
    # Проверяем PATH
    if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
        warning "Директория $BIN_DIR не в PATH"
        echo -e "${YELLOW}Добавьте в ~/.bashrc или ~/.zshrc:${NC}"
        echo -e "${GREEN}export PATH=\"\$PATH:$BIN_DIR\"${NC}"
    fi
}

# Тестирование установки
test_installation() {
    info "Тестирование установки..."
    
    cd "$INSTALL_DIR"
    if python3 -c "import json; json.load(open('training_data.json'))" 2>/dev/null; then
        success "Файлы данных корректны"
    else
        error "Проблема с файлами данных"
    fi
    
    if python3 -c "exec(open('artix_training.py').read())" --version 2>/dev/null; then
        success "Основной скрипт запускается"
    else
        warning "Возможны проблемы с основным скриптом"
    fi
}

# Вывод информации о завершении
finish_installation() {
    echo
    echo -e "${GREEN}╔══════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║${NC} ${CYAN}🎉 Установка успешно завершена!${NC}               ${GREEN}║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}"
    echo
    echo -e "${CYAN}📍 Местоположение:${NC} $INSTALL_DIR"
    echo -e "${CYAN}🚀 Запуск:${NC} $SCRIPT_NAME"
    echo -e "${CYAN}🔧 Прямой запуск:${NC} python3 $INSTALL_DIR/artix_training.py"
    echo
    echo -e "${YELLOW}💡 Полезные команды:${NC}"
    echo -e "   • ${GREEN}$SCRIPT_NAME${NC} - запуск тренажера"
    echo -e "   • ${GREEN}cd $INSTALL_DIR && git pull${NC} - обновление"
    echo
    echo -e "${PURPLE}📚 Документация: $INSTALL_DIR/README.md${NC}"
    echo -e "${PURPLE}🔍 Техдокументация: $INSTALL_DIR/TECHNICAL_DOCS.md${NC}"
}

# Основная функция
main() {
    # Проверяем права (не root)
    if [ "$EUID" -eq 0 ]; then
        warning "Не рекомендуется запускать установку от root"
        echo -e "${YELLOW}Продолжить? (y/N)${NC}"
        read -r answer
        if [[ ! $answer =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    check_dependencies
    get_install_dir
    install_files
    create_launcher
    test_installation
    finish_installation
}

# Обработка прерывания
trap 'echo -e "\n${RED}Установка прервана${NC}"; exit 1' INT

# Запуск основной функции
main "$@"