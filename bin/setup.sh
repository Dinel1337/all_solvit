#!/bin/bash
# setup.sh — автоматическая настройка окружения Solvit
# Запуск: curl -sSL https://raw.githubusercontent.com/yourusername/solvit/main/scripts/setup.sh | bash

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
    echo -e "${RED}❌ Docker не найден.${NC}"
    echo -e "   Установите Docker: https://docs.docker.com/engine/install/"
    exit 1
fi
echo -e "${GREEN}✓ Docker установлен${NC}"

# 2. Проверка Docker Compose (V2)
echo -e "${YELLOW}→ Проверка Docker Compose...${NC}"
if ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose не найден.${NC}"
    echo -e "   Установите: https://docs.docker.com/compose/install/"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose установлен${NC}"

# 3. Проверка uv (менеджер пакетов)
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

# 5. Клонирование или обновление репозитория
if [ ! -f "main.py" ]; then
    echo -e "${YELLOW}→ Клонирование репозитория...${NC}"
    git clone https://github.com/yourusername/solvit.git
    cd solvit
else
    echo -e "${GREEN}✓ Уже в репозитории solvit${NC}"
fi

# 6. Создание .env (если нет)
echo -e "${YELLOW}→ Настройка .env...${NC}"
if [ ! -f ".env" ]; then
    cat > .env << EOF
# Solvit Environment
SECRET_KEY=super_secret_key_$(openssl rand -hex 16 2>/dev/null || echo "test_key_123")
ALGORITHM=HS256
DATABASE_URL_asyncpg=postgresql+asyncpg://solvit:solvit@localhost:5432/solvit
DEBUG=True
TESTING=False
EOF
    echo -e "${GREEN}✓ .env создан${NC}"
else
    echo -e "${GREEN}✓ .env уже существует${NC}"
fi

# 7. Поднятие контейнеров (PostgreSQL и др.)
echo -e "${YELLOW}→ Запуск контейнеров (docker-compose up -d)...${NC}"
docker compose up -d
echo -e "${GREEN}✓ Контейнеры запущены${NC}"

# 8. Установка зависимостей Python через uv
echo -e "${YELLOW}→ Установка зависимостей...${NC}"
uv sync
echo -e "${GREEN}✓ Зависимости установлены${NC}"

# 9. Финальный вывод
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    ✅ Установка завершена!                 ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📌 Тестовый пользователь:${NC}"
echo -e "   Email: ${YELLOW}test@example.com${NC}"
echo -e "   Пароль: ${YELLOW}testpass${NC}"
echo ""
echo -e "${BLUE}🚀 Запуск проекта:${NC}"
echo -e "   ${GREEN}uv run python main.py -n 2${NC}"
echo ""
echo -e "${BLUE}📚 Документация API:${NC}"
echo -e "   ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo -e "${BLUE}🛑 Остановка контейнеров:${NC}"
echo -e "   ${GREEN}docker compose down${NC}"
echo ""

# этот баш я сделал через нейросеть()()()