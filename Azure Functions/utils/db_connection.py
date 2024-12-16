from azure.cosmos import CosmosClient

COSMOS_DB_ENDPOINT = "https://tollviolationdetectionsystemdbaccount.documents.azure.com:443/" 
COSMOS_DB_KEY = ""  

client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)


from jose import JWTError, jwt
import time

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"


def encode_token(data:dict):
    try:
        data = data.copy()
        data.update({'iat':time.time(),'exp': time.time()+3600})
        return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    except JWTError:
        raise JWTError("Error encoding token")
    
def decode_token(token:str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise JWTError("Error decoding token")