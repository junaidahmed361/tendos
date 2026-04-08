"""AES-256-GCM encryption for LoRA weight protection."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


class WeightEncryptor:
    """Encrypt and decrypt LoRA adapter weights using AES-256-GCM."""

    NONCE_SIZE = 12  # 96-bit nonce for GCM
    TAG_SIZE = 16  # 128-bit authentication tag

    def __init__(self, key: bytes) -> None:
        if len(key) != 32:
            raise ValueError("Key must be 32 bytes (AES-256)")
        self._key = key

    @staticmethod
    def generate_key() -> bytes:
        return os.urandom(32)

    def encrypt(self, plaintext: bytes) -> bytes:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM

        nonce = os.urandom(self.NONCE_SIZE)
        aead = AESGCM(self._key)
        ciphertext = aead.encrypt(nonce, plaintext, None)
        return nonce + ciphertext  # nonce || ciphertext || tag (tag appended by GCM)

    def decrypt(self, data: bytes) -> bytes:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM

        if len(data) < self.NONCE_SIZE + self.TAG_SIZE:
            raise ValueError("Data too short to contain nonce and tag")
        nonce = data[: self.NONCE_SIZE]
        ciphertext = data[self.NONCE_SIZE :]
        aead = AESGCM(self._key)
        return aead.decrypt(nonce, ciphertext, None)

    def encrypt_file(self, input_path: Path, output_path: Path) -> None:
        plaintext = input_path.read_bytes()
        output_path.write_bytes(self.encrypt(plaintext))

    def decrypt_file(self, input_path: Path, output_path: Path) -> None:
        data = input_path.read_bytes()
        output_path.write_bytes(self.decrypt(data))
