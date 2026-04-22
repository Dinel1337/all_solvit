#!/bin/bash
# setup.sh — автоматическая настройка окружения Solvit
# Запуск: curl -sSL https://raw.githubusercontent.com/Dinel1337/all_solvit/main/bin/setup.sh | bash

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                 Solvit — установка окружения              ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# 1. Проверка Docker
echo -e "${YELLOW}→ Проверка Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker не найден. Установите Docker: https://docs.docker.com/engine/install/${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker установлен${NC}"

# 2. Проверка Docker Compose V2
echo -e "${YELLOW}→ Проверка Docker Compose...${NC}"
if ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose не найден. Установите: https://docs.docker.com/compose/install/${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose установлен${NC}"

# 3. Проверка uv
echo -e "${YELLOW}→ Проверка uv...${NC}"
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}📦 Установка uv...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi
echo -e "${GREEN}✓ uv установлен${NC}"

# 4. Проверка Git
echo -e "${YELLOW}→ Проверка Git...${NC}"
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git не найден. Установите git${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Git установлен${NC}"

# 5. Клонирование репозитория (если не внутри all_solvit)
if [ ! -f "main.py" ] && [ ! -d "src" ]; then
    echo -e "${YELLOW}→ Клонирование репозитория...${NC}"
    git clone https://github.com/Dinel1337/all_solvit.git
    cd all_solvit
else
    echo -e "${GREEN}✓ Уже в репозитории all_solvit${NC}"
fi

# 6. Создание .env (только если отсутствует)
echo -e "${YELLOW}→ Настройка .env...${NC}"
if [ ! -f ".env" ]; then
    SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || echo "super_secret_key_$(date +%s%N | sha256sum | head -c 64)")
    cat > .env << EOF
HIDE_DEV_FILES=true

DB_USER=postgres
DB_PASSWORD=dinelefox
DB_HOST=postgres
DB_PORT=5432
DB_NAME=all_solvit

RESTART_PG=1

UVICORN_HOST=0.0.0.0
UVICORN_PORT=8000

SECRET_KEY=${SECRET_KEY}
ALGORITHM=HS256

TOKEN=7687868610:AAGtBS0RWt9MQiH7Y4qEkC4hy1yzATQzbCE
EOF
    echo -e "${GREEN}✓ .env создан${NC}"
else
    echo -e "${GREEN}✓ .env уже существует, пропускаем создание${NC}"
fi

# 7. Запуск контейнеров
echo -e "${YELLOW}→ Запуск контейнеров...${NC}"
docker compose up -d
echo -e "${GREEN}✓ Контейнеры запущены${NC}"

# 8. Установка зависимостей
echo -e "${YELLOW}→ Установка зависимостей...${NC}"
uv sync
echo -e "${GREEN}✓ Зависимости установлены${NC}"

# 9. Финальный вывод
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    ✅ Установка завершена!                 ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}🚀 Запуск проектов:${NC}"
echo -e "   ${GREEN}uv run python main.py -n 2${NC}   # API Tracker (порт 8000)"
echo -e "   ${GREEN}uv run python main.py -n 3${NC}   # Quiz Platform (порт 8001)"
echo -e "   ${GREEN}uv run python main.py -n 4${NC}   # Chat Bot Binance"
echo ""
echo -e "${BLUE}📚 Документация API:${NC}"
echo -e "   ${GREEN}http://localhost:8000/docs${NC}   # API Tracker"
echo -e "   ${GREEN}http://localhost:8001/docs${NC}   # Quiz Platform"
echo ""
echo -e "${BLUE}🛑 Остановка контейнеров:${NC}"
echo -e "   ${GREEN}docker compose down${NC}"
echo ""
sudo chown -R $USER:$USER $(find . -type d -name "__pycache__") 2>/dev/null