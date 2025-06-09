import subprocess
import os

DECRYPTOR_BIN = "./decrypt_payload"   
BLOB_PATH = "./system.txt"            

def decrypt_pbx(pbx_path: str) -> str:
    """Calls C binary to decrypt a .pbx file and return plaintext Python code."""
    if not os.path.exists(DECRYPTOR_BIN):
        raise FileNotFoundError(f"Decryptor binary not found: {DECRYPTOR_BIN}")
    if not os.path.exists(pbx_path):
        raise FileNotFoundError(f"PBX file not found: {pbx_path}")
    if not os.path.exists(BLOB_PATH):
        raise FileNotFoundError(f"Missing system.txt blob for key derivation")

    try:
        result = subprocess.run(
            [DECRYPTOR_BIN, pbx_path],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            raise RuntimeError(f"Decryption failed: {result.stderr.strip()}")

        return result.stdout

    except subprocess.TimeoutExpired:
        raise TimeoutError("Decryptor timed out")
