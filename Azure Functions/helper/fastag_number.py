import random
import string

def generate_dummy_fastag_id():
    prefix = ''.join(random.choices(string.ascii_uppercase, k=3))
    number = ''.join(random.choices(string.digits, k=10))
    fastag_id = prefix + number
    return fastag_id

if __name__== "__main__":
    dummy_fastag_id = generate_dummy_fastag_id()
    print(dummy_fastag_id)
