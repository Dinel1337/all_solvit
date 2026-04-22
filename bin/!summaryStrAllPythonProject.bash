
find . -name "*.py" \
    -not -path "./.venv/*" \
    -not -path "./.tox/*" \
    -not -path "./.mypy_cache/*" \
    -not -path "./.pytest_cache/*" \
    -not -path "./__pycache__/*" \
    -not -path "./build/*" \
    -not -path "./dist/*" \
    -not -path "./*.egg-info/*" \
    -not -path "./.eggs/*" \
    -not -path "./.ruff_cache/*" \
    -not -path "./.coverage/*" \
    -not -path "./htmlcov/*" \
    -not -path "./.cursor/*" \
    -not -path "./.vscode/*" \
    -not -path "./.idea/*" \
    -type f 2>/dev/null | xargs wc -l 2>/dev/null | tail -1