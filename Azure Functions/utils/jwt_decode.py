
from jose import JWTError, jwt
import time
import os

ALGORITHM = "RS256"

def encode_token(data:dict):
    try:
        data = data.copy() 
        data.update({'iat':time.time(),'exp': time.time()+3600})
        private_key = os.getenv("PRIVATE_KEY")

        return jwt.encode(data, private_key, algorithm=ALGORITHM)
    except JWTError:
        raise JWTError("Error encoding token")
    
def decode_token(token:str):
    try:
        public_key = os.getenv("PUBLIC_KEY")
        return jwt.decode(token, public_key, algorithms=[ALGORITHM])
    except JWTError:
        raise JWTError("Error decoding token")