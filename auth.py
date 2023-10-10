import bcrypt
from database import get_user

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(
        plain_password.encode('utf-8') if isinstance(plain_password, str) else plain_password,
        hashed_password.encode('utf-8') if isinstance(hashed_password, str) else hashed_password
    )

def authenticate_user(email: str, password: str):
    user = get_user(email)
    if user is None:
        return False
    print(user)
    if not verify_password(password, bytes.fromhex(user[1][2:])):
        return False
    return user
