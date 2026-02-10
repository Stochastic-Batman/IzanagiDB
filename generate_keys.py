import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend


output_dir = os.getcwd()

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

public_key = private_key.public_key()

# Serialize private key to PEM format
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

# Serialize public key to PEM format
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

private_path = os.path.join(output_dir, "private_key.pem")
public_path = os.path.join(output_dir, "public_key.pem")

with open(private_path, 'wb') as f:
    f.write(private_pem)
    print(f"Generated {private_path}")

with open(public_path, 'wb') as f:
    f.write(public_pem)
    print(f"Generated {public_path}")
