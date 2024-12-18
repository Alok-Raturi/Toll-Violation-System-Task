from bcrypt import hashpw, gensalt, checkpw
import re

PASSWORD_REGEX = "^(?=.*[A-Z].*[A-Z])(?=.*[!@#$&*])(?=.*[0-9].*[0-9])(?=.*[a-z].*[a-z].*[a-z]).{8}$"

PASSWORD_CONSTRAINT = """
Your password:\n
    - should have 2 uppercase characters\n
    - should have 1 special character\n
    - should have 2 digits\n
    - should have 3 lowercase characters\n
    - should have minimum length of 8 characters
"""

def hash_password(password: str) -> str:            
    return hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')        

def check_password(password: str, hashed_password: str) -> bool:               
    return checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def check_password_strength(password: str) -> bool:
    if re.match(PASSWORD_REGEX, password):
        return True
    return False