from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
path = Path('src')
src_path = [''] + [f.name for f in path.iterdir() if f.is_dir() and not f.name.startswith('_') and not f.name.startswith('.')]

DEBUG = False
ECHO = False

class CookieSetter:
    SECURE = False
    HTTPONLY = True
    SAMESITE = 'lax'
    MAX_AGE=3600*24*7

ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7