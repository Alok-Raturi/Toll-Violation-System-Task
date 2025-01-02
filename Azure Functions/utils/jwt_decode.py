
from jose import JWTError, jwt
import time
import os

ALGORITHM = "HS256"
SECRET_KEY = "Alok@123"

def encode_token(data:dict):
    try:
        data = data.copy() 
        data.update({'iat':time.time(),'exp': time.time()+3600})
        private_key = f'''{os.getenv('PRIVATE_KEY')}'''
        return jwt.encode(data, private_key, algorithm=ALGORITHM)
    except JWTError:
        raise JWTError("Error encoding token")
    
def decode_token(token:str):
    try:
        public_key = f'''{os.getenv("PUBLIC_KEY")}'''
        return jwt.decode(token, public_key, algorithms=[ALGORITHM])
    except JWTError:
        raise JWTError("Error decoding token")


# def encode_token(data:dict):
#     try:
#         data = data.copy() 
#         data.update({'iat':time.time(),'exp': time.time()+3600})
#         # private_key = f'''{os.getenv('PRIVATE_KEY')}'''
#         return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
#     except JWTError:
#         raise JWTError("Error encoding token")
    
# # abc = encode_token({"name":"Alok","class":"abc"})
# # print(abc)

# def decode_token(token:str):
#     try:
#         # public_key = f'''{os.getenv("PUBLIC_KEY")}'''
#         return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#     except JWTError:
#         raise JWTError("Error decoding token")


# print(decode_token("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiQWxvayIsImNsYXNzIjoiYWJjZCIsImlhdCI6MTczNTMwMDUyNi4zMTYzNDM1LCJleHAiOjE3MzUzMDQxMjYuMzE2MzQzNX0.X0OS3BNq3EEa53y07vT8AUFM2fvyo66nsOTInxG5PzU"))