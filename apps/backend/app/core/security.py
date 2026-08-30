import os
import sys
import json
import base64
import hashlib
from typing import Optional, Dict, Any
from pathlib import Path
from app.core.logging import logger

class TokenStorage:
    """
    Abstracao segura de armazenamento de tokens OAuth.
    Nunca grava tokens em texto plano no banco de dados SQLite.
    No Windows, utiliza DPAPI / CryptProtectData quando disponivel (via ctypes)
    com fallback para criptografia simetrica derivada de segredo de maquina e arquivo isolado no AppData.
    """
    def __init__(self):
        appdata = os.environ.get("APPDATA")
        if appdata:
            self.storage_dir = Path(appdata) / "Resolva" / "credentials"
        else:
            self.storage_dir = Path.home() / ".resolva" / "credentials"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._key = self._derive_machine_key()

    def _derive_machine_key(self) -> bytes:
        seed = f"resolva_secret_{os.environ.get('USERNAME', 'default')}_{os.environ.get('COMPUTERNAME', 'pc')}"
        return hashlib.sha256(seed.encode("utf-8")).digest()

    def _xor_cipher(self, data: bytes, key: bytes) -> bytes:
        return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

    def _encrypt(self, raw_str: str) -> str:
        if sys.platform == "win32":
            try:
                import ctypes
                from ctypes import wintypes

                class DATA_BLOB(ctypes.Structure):
                    _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_byte))]

                CryptProtectData = ctypes.windll.crypt32.CryptProtectData
                data_bytes = raw_str.encode("utf-8")
                blob_in = DATA_BLOB(len(data_bytes), ctypes.cast(ctypes.create_string_buffer(data_bytes), ctypes.POINTER(ctypes.c_byte)))
                blob_out = DATA_BLOB()

                if CryptProtectData(ctypes.byref(blob_in), "resolva_token", None, None, None, 0x01, ctypes.byref(blob_out)):
                    out_bytes = ctypes.string_at(blob_out.pbData, blob_out.cbData)
                    ctypes.windll.kernel32.LocalFree(blob_out.pbData)
                    return "dpapi:" + base64.b64encode(out_bytes).decode("ascii")
            except Exception as e:
                logger.debug(f"DPAPI protect fallback: {e}")

        raw_bytes = raw_str.encode("utf-8")
        encrypted = self._xor_cipher(raw_bytes, self._key)
        return "enc:" + base64.b64encode(encrypted).decode("ascii")

    def _decrypt(self, enc_str: str) -> str:
        if enc_str.startswith("dpapi:") and sys.platform == "win32":
            try:
                import ctypes
                from ctypes import wintypes

                class DATA_BLOB(ctypes.Structure):
                    _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_byte))]

                CryptUnprotectData = ctypes.windll.crypt32.CryptUnprotectData
                enc_bytes = base64.b64decode(enc_str[6:])
                blob_in = DATA_BLOB(len(enc_bytes), ctypes.cast(ctypes.create_string_buffer(enc_bytes), ctypes.POINTER(ctypes.c_byte)))
                blob_out = DATA_BLOB()

                if CryptUnprotectData(ctypes.byref(blob_in), None, None, None, None, 0x01, ctypes.byref(blob_out)):
                    out_bytes = ctypes.string_at(blob_out.pbData, blob_out.cbData)
                    ctypes.windll.kernel32.LocalFree(blob_out.pbData)
                    return out_bytes.decode("utf-8")
            except Exception as e:
                logger.debug(f"DPAPI unprotect fallback: {e}")

        if enc_str.startswith("enc:"):
            enc_bytes = base64.b64decode(enc_str[4:])
            decrypted = self._xor_cipher(enc_bytes, self._key)
            return decrypted.decode("utf-8")
        
        return enc_str

    def _get_account_file(self, account_id: int) -> Path:
        return self.storage_dir / f"acc_{account_id}.vault"

    async def save_tokens(self, account_id: int, tokens: Dict[str, Any]) -> None:
        serialized = json.dumps(tokens)
        encrypted = self._encrypt(serialized)
        file_path = self._get_account_file(account_id)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(encrypted)

    async def get_tokens(self, account_id: int) -> Optional[Dict[str, Any]]:
        file_path = self._get_account_file(account_id)
        if not file_path.exists():
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                encrypted = f.read().strip()
            decrypted = self._decrypt(encrypted)
            return json.loads(decrypted)
        except Exception as e:
            logger.error(f"Erro ao recuperar tokens para conta {account_id}: {e}")
            return None

    async def delete_tokens(self, account_id: int) -> bool:
        file_path = self._get_account_file(account_id)
        if file_path.exists():
            try:
                file_path.unlink()
                return True
            except Exception as e:
                logger.error(f"Erro ao deletar tokens da conta {account_id}: {e}")
                return False
        return True

token_storage = TokenStorage()
