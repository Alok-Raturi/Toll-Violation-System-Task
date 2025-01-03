import time
from jose import JWTError
from utils.jwt_decode import decode_token


def user_middleware(token:str, designation: str):
    try:
        if token.startswith("Bearer "):
            token = token.split(" ")[1]
        data = decode_token(token)
        if data['designation'] != designation:
            return False
        if data['exp'] < time.time():
            return False
        return data
    except JWTError:
        return False