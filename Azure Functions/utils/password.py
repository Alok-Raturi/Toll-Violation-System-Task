from bcrypt import hashpw, gensalt, checkpw
import re
import logging

PASSWORD_REGEX = "^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=])(?=\S+$).{8,20}$"

PASSWORD_CONSTRAINT = """
Your password:\n
    - should have at least 1 uppercase characters\n
    - should have at least 1 special character - ?=.*[@#$%^&+=]\n
    - should have at least 1 digits\n
    - should have at least 1 lowercase characters\n
    - should not contain any whitespace characters\n
    - should have minimum length of 8 characters and max length of 20 characters
"""

def hash_password(password: str) -> str:            
    return hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')        
            
def check_password(password: str, hashed_password: str) -> bool:     
    logging.warning("Checking password")          
    return checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def check_password_strength(password: str) -> bool:
    if re.match(PASSWORD_REGEX, password):
        return True
    return False