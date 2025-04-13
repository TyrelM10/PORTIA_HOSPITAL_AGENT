from cryptography.fernet import Fernet
import os

def encrypt_file(input_path, output_path, key_path="fernet_key.txt"):
    # Load or generate key
    if os.path.exists(key_path):
        with open(key_path, 'rb') as f:
            key = f.read()
    else:
        key = Fernet.generate_key()
        with open(key_path, 'wb') as f:
            f.write(key)

    cipher = Fernet(key)

    with open(input_path, 'rb') as file:
        data = file.read()

    encrypted_data = cipher.encrypt(data)

    with open(output_path, 'wb') as enc_file:
        enc_file.write(encrypted_data)

    print(f"✅ Transcript encrypted and saved to {output_path}")
    return output_path
