import os
import time
import json
import zlib
import struct
import random
import hashlib
from Crypto.Cipher import AES
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

# ===== M25 Encrypt API =====

def create_mapping(seed):
    random.seed(seed)
    original = list(range(256))
    shuffled = original[:]
    random.shuffle(shuffled)
    return dict(zip(original, shuffled))

def inverse_mapping(mapping):
    return {v: k for k, v in mapping.items()}

def apply_mapping(data: bytes, mapping: dict) -> bytes:
    return bytes([mapping[b] for b in data])

def derive_key(password: str, salt: bytes, iterations=100_000):
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations, dklen=32)

def aes192_encrypt(data: bytes, key: bytes) -> bytes:
    cipher = AES.new(key[:24], AES.MODE_ECB)
    pad_len = 16 - len(data) % 16
    data += bytes([pad_len] * pad_len)
    return cipher.encrypt(data)

def aes192_decrypt(data: bytes, key: bytes) -> bytes:
    cipher = AES.new(key[:24], AES.MODE_ECB)
    decrypted = cipher.decrypt(data)
    pad_len = decrypted[-1]
    return decrypted[:-pad_len]

def chacha20_encrypt(data: bytes, key: bytes, nonce: bytes) -> bytes:
    chacha = ChaCha20Poly1305(key)
    return chacha.encrypt(nonce, data, None)

def chacha20_decrypt(data: bytes, key: bytes, nonce: bytes) -> bytes:
    chacha = ChaCha20Poly1305(key)
    return chacha.decrypt(nonce, data, None)

def m25_encrypt(data: bytes, password: str) -> bytes:
    salt = os.urandom(16)
    nonce = os.urandom(12)
    rand1 = random.randint(1, 2**31 - 1)
    rand2 = random.randint(1, 2**31 - 1)

    map1 = create_mapping(rand1)
    map2 = create_mapping(rand2)

    stage0 = apply_mapping(data, map1)
    stage1 = apply_mapping(stage0, map2)

    key = derive_key(password, salt)
    stage2 = aes192_encrypt(stage1, key)
    stage3 = chacha20_encrypt(stage2, key, nonce)

    return rand1.to_bytes(4, 'big') + rand2.to_bytes(4, 'big') + salt + nonce + stage3

def m25_decrypt(blob: bytes, password: str) -> bytes:
    rand1 = int.from_bytes(blob[0:4], 'big')
    rand2 = int.from_bytes(blob[4:8], 'big')
    salt = blob[8:24]
    nonce = blob[24:36]
    encrypted = blob[36:]

    key = derive_key(password, salt)
    stage2 = chacha20_decrypt(encrypted, key, nonce)
    stage1 = aes192_decrypt(stage2, key)

    map2 = create_mapping(rand2)
    map1 = create_mapping(rand1)
    unmap2 = inverse_mapping(map2)
    unmap1 = inverse_mapping(map1)

    stage0 = apply_mapping(stage1, unmap2)
    original = apply_mapping(stage0, unmap1)
    return original

# ===== BT1 Public API =====

def bt1_pack_file(input_path: str, output_path: str, password: str = "test1"):
    with open(input_path, 'rb') as f:
        original = f.read()

    compressed = zlib.compress(original)
    metadata = {
        "filename": os.path.basename(input_path),
        "compressed_size": len(compressed),
        "original_size": len(original),
        "created": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "encryptor": "M25-v1"
    }

    metadata_json = json.dumps(metadata).encode()
    metadata_compressed = zlib.compress(metadata_json)
    encrypted = m25_encrypt(compressed, password)

    with open(output_path, 'wb') as f:
        f.write(b'BT1\x00')
        f.write(struct.pack(">I", len(metadata_compressed)))
        f.write(metadata_compressed)
        f.write(encrypted)

def bt1_unpack_file(input_path: str, output_folder: str, password: str = "test1"):
    with open(input_path, 'rb') as f:
        if f.read(4) != b'BT1\x00':
            raise ValueError("Invalid BT1 format.")

        meta_len = struct.unpack(">I", f.read(4))[0]
        metadata = json.loads(zlib.decompress(f.read(meta_len)))
        encrypted = f.read()

    decrypted = m25_decrypt(encrypted, password)
    original = zlib.decompress(decrypted)

    output_path = os.path.join(output_folder, metadata["filename"])
    with open(output_path, 'wb') as f:
        f.write(original)

# ===== CLI usable =====
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage:")
        print("  Pack  : python bt1module.py pack <input_file> <output_file.bt1>")
        print("  Unpack: python bt1module.py unpack <input.bt1> <output_folder>")
        exit(1)

    mode = sys.argv[1]
    if mode == "pack":
        bt1_pack_file(sys.argv[2], sys.argv[3])
        print(f"[✔] Packed: {sys.argv[3]}")
    elif mode == "unpack":
        bt1_unpack_file(sys.argv[2], sys.argv[3])
        print(f"[✔] Unpacked to: {sys.argv[3]}")
    else:
        print("Invalid syntax. Use 'pack' or 'unpack'.")

