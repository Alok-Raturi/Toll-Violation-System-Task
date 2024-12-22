import re
import logging
import email_validator as ev

logger = logging.getLogger() 

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

def validate_password(password):
    if not re.match(PASSWORD_REGEX, password):
        logger.error("Password does not meet the required constraints.")
        print(f"Your password does not meet the following constraints.\n{PASSWORD_CONSTRAINT}")
        return False
    print("Password Validation Successful.")
    logger.info("Password validation successful.")
    return True


def validate_email_input(email):
    try:
        ev.validate_email(email)
        print("Email validation successful.")
        logger.info(f"Email validation successful for: {email}")
    except ev.EmailNotValidError:
        logger.error(f"Invalid email entered: {email}")
        print("Email is not valid...\n")
        return False
    return True
