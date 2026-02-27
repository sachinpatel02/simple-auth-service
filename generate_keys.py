# generate_keys.py
import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Ensure the keys directory exists
os.makedirs("keys", exist_ok=True)

# Generate Private Key (2048-bit is the industry standard baseline for RS256)
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

# Extract Public Key
public_key = private_key.public_key()

# Save Private Key to file
with open("keys/private.pem", "wb") as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))

# Save Public Key to file
with open("keys/public.pem", "wb") as f:
    f.write(public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ))

print("Keys generated successfully in the 'keys/' directory!")
print("CRITICAL: Add 'keys/' to your .gitignore right now.")