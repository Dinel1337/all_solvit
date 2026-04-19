import asyncio
from src._core.error_handler.setup import setup_exception_handlers
from src._core.auth import setup_control   
from .app import create_app

app = create_app()

@setup_control(app, [], [], port=8001)
async def main():
    setup_exception_handlers(app)

def run():
    """Точка входа для запуска из внешнего модуля (main.py)"""
    asyncio.run(main())

if __name__ == '__main__':
    asyncio.run(main())  # для прямого запуска