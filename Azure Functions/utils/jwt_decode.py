
from jose import JWTError, jwt
import time
import os
import requests


ALGORITHM = "RS256"

headers = {
    "alg": "RS256", 
    "typ": "JWT",   
    "kid": "a1b1"
}

def get_public_key(token:str):
    header = jwt.get_unverified_headers(token)
    kid = header['kid']
    print(header)
    payload = jwt.get_unverified_claims(token)
    print(payload)
    
    url = payload['url']
    response = requests.get(url).json()
    public_key = [item for item in response if item['kid'] == kid]
    return public_key[0]['public-key']

def encode_token(data:dict):
    try:
        data = data.copy() 
        data.update({
            "iat":time.time(),
            "exp": time.time()+3600,
            "url": "https://67725c51ee76b92dd4920815.mockapi.io/well-known/jwks/public-key"
        })
        private_key = f'''{os.getenv('PRIVATE_KEY')}'''
        return jwt.encode(data, private_key, algorithm=ALGORITHM,headers=headers)
    except JWTError:
        raise JWTError("Error encoding token")

def decode_token(token:str):
    try:
        public_key = f'''{get_public_key(token)}'''
        return jwt.decode(token, public_key, algorithms=[ALGORITHM])
    except JWTError:
        raise JWTError("Error decoding token")

