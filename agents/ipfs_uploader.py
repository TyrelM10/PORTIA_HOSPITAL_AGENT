import os
import requests
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

PINATA_API_KEY = os.getenv("PINATA_API_KEY")
PINATA_SECRET_API_KEY = os.getenv("PINATA_SECRET_API_KEY")

def upload_to_ipfs(file_path):
    # 🔐 Step 1: Encrypt the file
    with open(file_path, 'rb') as f:
        data = f.read()
    
    key = Fernet.generate_key()
    cipher = Fernet(key)
    encrypted_data = cipher.encrypt(data)

    encrypted_path = f"/tmp/encrypted_{os.path.basename(file_path)}"
    with open(encrypted_path, "wb") as enc_file:
        enc_file.write(encrypted_data)

    # 🔗 Step 2: Upload encrypted file to IPFS via Pinata
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {
        "pinata_api_key": PINATA_API_KEY,
        "pinata_secret_api_key": PINATA_SECRET_API_KEY
    }

    try:
        with open(encrypted_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(url, files=files, headers=headers)
        
        response.raise_for_status()
        ipfs_hash = response.json()["IpfsHash"]

        # ✅ Use ipfs.io public gateway (more reliable than pinata.cloud)
        ipfs_link = f"http://127.0.0.1:8080/ipfs/{ipfs_hash}"


        print(f"🔗 Uploaded to IPFS: {ipfs_link}")
        return ipfs_link, key.decode()  # Return both link + encryption key

    except Exception as e:
        print(f"❌ IPFS Upload Failed: {e}")
        return None, None
