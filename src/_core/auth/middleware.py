from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.requests import Request

class AuthTokenMiddleware(BaseHTTPMiddleware):
    """Универсальный middleware - только достаёт токен"""
    
    async def dispatch(self, request: Request, call_next):
        token = request.cookies.get('access_token')
        
        if not token:
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        request.state.token = token
        response = await call_next(request)
        
        if response.status_code == 204:
            response.body = b''
            response.headers['content-length'] = '0'
        
        return response