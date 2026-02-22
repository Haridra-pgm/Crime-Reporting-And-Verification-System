# encryption.py
from cryptography.fernet import Fernet
import os
from cryptography.fernet import InvalidToken

# Specify the full path for the key to be saved in the 'app/util' directory
KEY_FILE = os.path.join(os.path.dirname(__file__), "secret.key")

def generate_and_save_key():
    """Generate and save the key once"""
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
        print(f"Key saved to {KEY_FILE}.")
    else:
        print("Key already exists.")

def load_key():
    """Load the key from the file"""
    
    if not os.path.exists(KEY_FILE):
        raise FileNotFoundError(f"Key file {KEY_FILE} not found. Generate the key first.")
    with open(KEY_FILE, "rb") as key_file:
        return key_file.read()

# Encrypt and Decrypt functions
def encrypt_message(message):
    generate_and_save_key()
    key = load_key()
    cipher_suite = Fernet(key)
    return cipher_suite.encrypt(message.encode())

def decrypt_message(encrypted_message):
    generate_and_save_key()
    key = load_key()
    cipher_suite = Fernet(key)
    # Accept either bytes or str for the token
    try:
        if isinstance(encrypted_message, str):
            token = encrypted_message.encode()
        else:
            token = encrypted_message
        return cipher_suite.decrypt(token).decode()
    except InvalidToken:
        # Token is invalid or corrupted (possibly stored plaintext or different key)
        print("[WARNING] Invalid encryption token provided to decrypt_message.")
        return None
    except Exception as e:
        # Generic fallback - log and return None
        print(f"[ERROR] Exception while decrypting message: {e}")
        return None
