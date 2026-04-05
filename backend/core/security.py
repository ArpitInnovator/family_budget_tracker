from datetime import datetime, timezone, timedelta
import os
from typing import Any, Dict
from dotenv import load_dotenv
import jwt # type: ignore
from fastapi import HTTPException
from uuid import UUID
from jose import JWTError, ExpiredSignatureError
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set") 

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440 


def create_access_token(*, user_id: UUID, role: str) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload: Dict[str, Any] = {"sub": str(user_id), "role": role, "exp": exp}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM) 

def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
    except ExpiredSignatureError:
     raise HTTPException(status_code=401, detail="Token expired")

    except JWTError:
     raise HTTPException(status_code=401, detail="Invalid token")
