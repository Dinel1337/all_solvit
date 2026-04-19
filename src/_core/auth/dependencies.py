import asyncio
import uvicorn
import subprocess
from dotenv import load_dotenv

load_dotenv()
from src.config import KILL_ROUTER, configAPI

from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import Request, FastAPI, Depends

from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from ..exceptions import TokenUnauthorized

from ..repositories import UserRepository
from ..schemas import UserInDB
from ..database import get_db

from typing import List, Optional

async def token_dispatch(
    request: Request,
    db: AsyncSession
):
    """Создан для извлечение юзера из токена"""
    token = request.state.token
    if not token:
        raise TokenUnauthorized(None, message='Отсутсвует токен')
    
    from ..services import UserService
    
    service = UserService(UserRepository(db))
    user = await service.get_user(token=token)
    if user:
        return UserInDB.model_validate(user)
    raise TokenUnauthorized(token, message='Неправильный токен')

def debug_kill_router(app: FastAPI):
    """Декоратор для добавления /kill эндпоинта в режиме DEBUG"""
    def decorator(func):
        if KILL_ROUTER:
            @app.get('/kill')
            async def kill_project(request: Request):
                await asyncio.sleep(0.1)
                import os, signal
                os.kill(os.getpid(), signal.SIGINT)
        app.router.routes[-1].tags = ['Убить проект']
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def setup_control(
    APP: FastAPI,
    routers: List,
    middlewares: list,
    cfg: uvicorn.Config = configAPI,
    port: int = 8000,
    metric:Optional[str] = None
):
    def flatten_routers(routers_list):
        result = []
        for item in routers_list:
            if isinstance(item, list):
                result.extend(flatten_routers(item))
            else:
                result.append(item)
        return result
    
    def decorator(func):
        async def wrapper(*args, **kwargs):
            flat_routers = flatten_routers(routers)
            for r in flat_routers:
                if isinstance(r, FastAPI):
                    for route in r.routes:
                        APP.include_router(route)
                else:
                    APP.include_router(r)
            
            for m in middlewares:
                APP.add_middleware(m)
            
            if func:
                await func(*args, **kwargs)
            
            try:
                subprocess.run(
                    f"fuser -k {port}/tcp 2>/dev/null",
                    shell=True,
                    capture_output=True
                )
                print(f"Порт {port} освобождён (если был занят)")
            except Exception as e:
                print(f"Не удалось очистить порт: {e}")
            if metric:
                Instrumentator().instrument(APP).expose(APP, endpoint=metric)
                APP.add_middleware(TrustedHostMiddleware, 
                                   allowed_hosts=["localhost", "127.0.0.1", "0.0.0.0"])

            config = cfg
            config.app = APP
            config.port = port
            config.host = '0.0.0.0'
            server = uvicorn.Server(config)
            await server.serve()
        
        return wrapper
    return decorator

async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    return await token_dispatch(request, db)