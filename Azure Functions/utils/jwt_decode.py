
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
        private_key = f'''-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDDW+zlhkJWFM7l\n3wogfndf/9a4qQpXaPWLbRFSyGOJ3CyiizMVx8oCFyDNwjOf3gVR3Kr+wumRJUdr\n+2yQkKP+djal9WGKqG3+teh+AhzOa4vMJZUJHD4X2LMk7sPKWJm9ZS5F3BUYakSe\n5ZBQdzc7PP4ClLnoOI3GXVijj5LWIBX5MNaXWqtobS8uk3fFW8uqF7hN2BWeL/I/\n1n25FIez5StBRvOyXxQw6WlbiIXcnAoSXajwBjqPYYElhj9M3mL3LkZERA0KOKmB\n9UHrXlvQuGwvqM+qz1A4JcVjRzJCqI2Z0BkOeuuzRPpjq1nLO32DKDBslZGi+Rz8\n1P99/0ExAgMBAAECggEAJcAFrvSarPeoY1MOKelGOA6/9z7y+KEXkbGpv01prqIV\nHfO4E2Vf67d8Z0Y3o5TLgl4ZzNDtQVbqzjrvZ6ALkIhXVwprpteVKbsNCgxudJTj\nlrdMbU4/0WvWcjSRMPCeBLMgle9JREaErA/AK0xeJ9xJWUZUBkOnYcV382MzBJ0n\npp4dl8T8KrgQuvn1yVR6Va+BO+Q0EOnjZSP4NmqcQ0XYy4CjoBUmYO57TYnU117q\nsoWrMTDbbd+3p1s41ojjgwNNF4bDpCVBz5mwq3SQ+6eIEjzsQigYkMQ2LZiLaDS8\nDkattNFe9ZXSLxrjKMP/oKoToL+KqE5gIkNgKEh4gQKBgQDHu3cZgu/zqgcjqde3\nEzOr32tIZRi4mjUB44iIpOOeUCOwqZmqnmryiBnNu7+4mMlJvrvN0QIyyp4m7ChP\nbeC9j2TvclcKZ7pVmdFCXUF8h2eU3KjIS5wHN2fvS7p1XbZK27hIhuNkF98/4bAE\nABxrl+wsT5HcjiC27EpHf1t6ZQKBgQD6ZRF3bAQb2nO4qEHNPlIYy0iEYPS7MaBK\nIkKwyRjC8YpAL1byDxYfmIp39wIp57rGcWGJzMfwgb+Fa+03Jz50Kgi7BzcDYm9U\nSzQAvq8jNB7Le6bz0pRC1xVY4rGW4BeIDw8AU9xYaAk6+WOY/pCWmGZ2EU6DmUWM\ns85uA/a43QKBgQCReCQCXK9PFKMmgmkuWbnkkFCe5aLfsNCyk3m5q/5sK4oS/TOC\nZOcXxbClevzkAcN5BoXaHUQwogoV5yJk1248Idgt3WUvmuTHu8QBRdKQVD5I2X3E\ng+0cBGqaitk+6gX+95B8omGzYP+kk0eTYlFQu9GzZDCkJpAFKovfDw8dUQKBgDRK\nIumjfwAqEHyBdqxb1V0kJpKuhK0K4gRZP0AX3rnnIw3gVPHbwKz8d/4xcRw7Lj/+\nsXXLc/1/uvUr4q/f3CT6GjSkfxKP3dvmkIePSpe5bKzlt6m3UgrbS7PyM0/koEVj\nj6hr2toDb9oG9oueraclUFBbsN++hE2rxvImlcFpAoGBAL+uD1ULUXiQ6rH8jQUY\n5LFzV/vFp5xwFpUPkYFkN3o/3t+1R1Wlv3chHjWbaH4PcfRL9jVEFHLSlIslkQ1D\nfo2YBWl0q0xA7oEm8SYlq4C4K4iOPQRpjX2BNXLa7WHTPVWpbjzlskDm+s1x3jql\nmS6ddlwjUy5m2dKtmLCBfs8z\n-----END PRIVATE KEY-----\n'''
        return jwt.encode(data, private_key, algorithm=ALGORITHM,headers=headers)
    except JWTError:
        raise JWTError("Error encoding token")

def decode_token(token:str):
    try:
        public_key = f'''{get_public_key(token)}'''
        return jwt.decode(token, public_key, algorithms=[ALGORITHM])
    except JWTError:
        raise JWTError("Error decoding token")

