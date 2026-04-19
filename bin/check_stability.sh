# использование: bash bin/check_stability.sh [количество_запусков]

RUNS=${1:-10}
PASSED=0

echo "Запуск тестов $RUNS раз..."
echo "================================"

for i in $(seq 1 $RUNS); do
    printf "[%2d/%2d] " $i $RUNS
    
    if pytest tests/ > /dev/null 2>&1; then
        echo "✅ PASSED"
        ((PASSED++))
    else
        echo "❌ FAILED"
    fi
done

echo "================================"
echo "Результат: $PASSED / $RUNS успешно"
echo "Стабильность: $(( PASSED * 100 / RUNS ))%"