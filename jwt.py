from jose import  jwt
from datetime import datetime, timedelta
from typing import Optional

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

def create_new_token():
    expiration = datetime.utcnow() + timedelta(seconds=10)
    to_encode = {"exp": expiration}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
