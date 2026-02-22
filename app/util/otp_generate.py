import secrets
import string

def generate_otp():
    characters = string.ascii_lowercase + string.digits
    otp = ''.join(secrets.choice(characters) for _ in range(6))
    return otp