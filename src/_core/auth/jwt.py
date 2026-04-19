from dotenv import load_dotenv
import os
load_dotenv()
import jwt 
from datetime import datetime, timezone, timedelta
from global_config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS

secret_key = os.getenv('SECRET_KEY')
algorithm = os.getenv('ALGORITHM')

def create_access_token(user_id: int):
    
    token_payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": datetime.now(timezone.utc)
    }  
    
    return jwt.encode(token_payload, secret_key, algorithm=algorithm)

def create_refresh_token(user_id: int) -> str:
    expires_delta = timedelta(REFRESH_TOKEN_EXPIRE_DAYS)
    expire = datetime.now(timezone.utc) + expires_delta
    
    payload = {
        "user_id": user_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    
    encoded_jwt = jwt.encode(payload, secret_key, algorithm=algorithm)
    return encoded_jwt    