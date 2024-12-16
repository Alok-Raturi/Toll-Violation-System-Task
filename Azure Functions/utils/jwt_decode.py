
from jose import JWTError, jwt
import time

SECRET_KEY = "mysecretkey"
ALGORITHM = "RS256"

def encode_token(data:dict):
    try:
        data = data.copy() 
        data.update({'iat':time.time(),'exp': time.time()+3600})
        with open('private_key.pem', 'r') as file:
            private_key = file.read()

        return jwt.encode(data, private_key, algorithm=ALGORITHM)
    except JWTError:
        raise JWTError("Error encoding token")
    
def decode_token(token:str):
    try:
        with open('public_key.pem', 'r') as file:
            public_key = file.read()
        return jwt.decode(token, public_key, algorithms=[ALGORITHM])
    except JWTError:
        raise JWTError("Error decoding token")