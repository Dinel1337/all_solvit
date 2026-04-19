#!/bin/!toggle_bash_view

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SETTINGS_DIR=".vscode"
SETTINGS_FILE="$SETTINGS_DIR/settings.json"

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}   VS Code File Visibility Toggle  ${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""

if [ -f "$SETTINGS_FILE" ] && grep -q '"files.exclude"' "$SETTINGS_FILE" && grep -q '"bin": true' "$SETTINGS_FILE"; then
    echo -e "${YELLOW}📁 Текущий статус: ${RED}СЛУЖЕБНЫЕ ФАЙЛЫ СКРЫТЫ${NC}"
else
    echo -e "${YELLOW}📁 Текущий статус: ${GREEN}ПОЛНАЯ СТРУКТУРА ВИДНА${NC}"
fi

echo ""
echo -e "${BLUE}Что вы хотите сделать?${NC}"
echo -e "  ${GREEN}y${NC}) Показать полную структуру (все файлы видны)"
echo -e "  ${RED}n${NC}) Скрыть служебные файлы (чистый вид)"
echo -e "  ${YELLOW}q${NC}) Выйти без изменений"
echo ""

read -p "Ваш выбор (y/n/q): " choice

case $choice in
    y|Y)
        echo -e "${GREEN}✓ Показываем полную структуру...${NC}"
        if [ -f "$SETTINGS_FILE" ]; then
            cp "$SETTINGS_FILE" "$SETTINGS_FILE.bak"
            python3 << 'EOF'
import json
import os

settings_file = ".vscode/settings.json"
if os.path.exists(settings_file):
    with open(settings_file, 'r') as f:
        try:
            settings = json.load(f)
        except:
            settings = {}
    
    if 'files.exclude' in settings:
        del settings['files.exclude']
    
    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=4)
EOF
            echo -e "${GREEN}✓ Все файлы теперь будут видны${NC}"
        else
            echo -e "${GREEN}✓ Уже в режиме полной структуры${NC}"
        fi
        ;;
    n|N)
        echo -e "${RED}✓ Скрываем служебные файлы...${NC}"
        mkdir -p "$SETTINGS_DIR"
        
        python3 << 'EOF'
import json
import os

settings_file = ".vscode/settings.json"
settings = {}

# Загружаем существующие настройки если есть
if os.path.exists(settings_file):
    with open(settings_file, 'r') as f:
        try:
            settings = json.load(f)
        except:
            settings = {}

# Добавляем files.exclude
settings['files.exclude'] = {
    "**/__pycache__": True,
    "**/.pytest_cache": True,
    ".venv": True,
    "bin": True,
    "tox.ini": True,
    "poetry.lock": True,
    "pyproject.toml": True,
    ".env": True,
    "Dockerfile": True,
    ".gitignore": True,
    ".coveragerc": True,
    "README.md": True,
    ".vscode": True
}

# Сохраняем
with open(settings_file, 'w') as f:
    json.dump(settings, f, indent=4)
EOF
        echo -e "${RED}✓ Служебные файлы будут скрыты${NC}"
        ;;
    q|Q)
        echo -e "${YELLOW}👋 Выход без изменений${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}❌ Неверный выбор!${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}📌 Для применения изменений:${NC}"
echo -e "   Нажмите ${YELLOW}Ctrl+Shift+P${NC} и выполните ${GREEN}Developer: Reload Window${NC}"
echo ""
clear