#!/bin/bash

# Подсчет символов в .py файлах, исключая виртуальное окружение и кэши

# echo "Подсчет символов в Python файлах..."

# Первая команда: очистка __pycache__ (опционально, можно закомментировать)
# echo "Очистка __pycache__ директорий..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Подсчет символов (wc -m вместо wc -l)
total_chars=$(find . -name "*.py" \
    -not -path "./.venv/*" \
    -not -path "./.pytest_cache/*" \
    -not -path "./.vscode/*" \
    -exec cat {} + | wc -m)

# echo "Общее количество символов в .py файлах: $total_chars"

file_count=$(find . -name "*.py" \
    -not -path "./.venv/*" \
    -not -path "./.pytest_cache/*" \
    -not -path "./.vscode/*" | wc -l)

# echo "Количество .py файлов: $file_count"

total_chars_no_spaces=$(find . -name "*.py" \
    -not -path "./.venv/*" \
    -not -path "./.pytest_cache/*" \
    -not -path "./.vscode/*" \
    -exec cat {} + | tr -d ' \t\n\r' | wc -m)

echo "Символы: $total_chars_no_spaces"