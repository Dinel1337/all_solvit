import sys
import argparse
import logging
import asyncio
import os
import subprocess

from global_config import src_path, DEBUG
from src._core import formater_console

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--number', type=int, choices=range(1, len(src_path)))
parser.add_argument('-i', '--info', action='store_true', help='Информация о проектах')
parser.add_argument('--init-db', action='store_true', help='Инициализировать базу данных и выйти')
parser.add_argument('-t', '--terminal', action='store_true', help='Запуск в терминале (не Docker)')

logging.basicConfig(
    level=logging.INFO if DEBUG else logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# @formater_console
def setup_environment(terminal_mode: bool):
    """Устанавливает переменные окружения и удаляет кэш модулей конфигурации."""
    if terminal_mode:
        print("Запуск в терминальном режиме (не через Docker)")
        os.environ['DB_HOST'] = '127.0.0.1'
        os.environ['DB_PORT'] = '5432'
        os.environ['DB_USER'] = 'postgres'
        os.environ['DB_PASSWORD'] = 'dinelefox'
        os.environ['DB_NAME'] = 'all_solvit'
        os.environ['UVICORN_HOST'] = '127.0.0.1'
    else:
        from dotenv import load_dotenv
        load_dotenv()

    for mod in list(sys.modules.keys()):
        if mod.startswith('src.config') or mod.startswith('src._core.database'):
            sys.modules.pop(mod, None)

@formater_console
def main():
    args = parser.parse_args()
    setup_environment(terminal_mode=args.terminal)

    from src._core.database import init_db, PublicBase, ApiTrackerBase, QuizPlatformBase

    async def initialize_all_schemas():
        try:
            await init_db(PublicBase)
            await init_db(ApiTrackerBase)
            await init_db(QuizPlatformBase)
            print("✅ Все схемы базы данных успешно инициализированы")
        except Exception as e:
            logger.error(f"Ошибка инициализации БД: {e}")
            raise

    def run_initialization():
        asyncio.run(initialize_all_schemas())

    if args.init_db:
        run_initialization()
        sys.exit(0)

    if len(sys.argv) == 1:
        print("Использование: python main.py <-n номер проекта>")
        print("Вывод доступных проектов: python main.py -i | --info")
        print("Инициализация БД: python main.py --init-db")
        print("Для локального запуска без Docker: python main.py -t -n <номер>")
        sys.exit(1)

    if args.info:
        for index, word in enumerate(src_path[1:], 1):
            print(f'{index} --> {word}')
        sys.exit(1)

    project = str(src_path[args.number]).strip()
    
    try:
        asyncio.run(init_db(PublicBase))
    except Exception as e:
        logger.error(f"Не удалось инициализировать PublicBase: {e}")
        sys.exit(1)

    cmd = [sys.executable, '-c', f'from src.{project}.main import run; run()']
    if args.terminal:
        cmd.append('-t')
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n Проект остановлен")
    except Exception as e:
        logger.error(f"Ошибка запуска проекта: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()