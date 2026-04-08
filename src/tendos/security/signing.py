"""Ed25519 cartridge signing and verification."""

from __future__ import annotations

from typing import TYPE_CHECKING

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)

if TYPE_CHECKING:
    from pathlib import Path


class KeyPair:
    """Ed25519 key pair for cartridge signing."""

    def __init__(
        self,
        private_key: Ed25519PrivateKey | None,
        public_key: Ed25519PublicKey,
    ) -> None:
        self._private_key = private_key
        self._public_key = public_key

    @classmethod
    def generate(cls) -> KeyPair:
        private = Ed25519PrivateKey.generate()
        return cls(private_key=private, public_key=private.public_key())

    @classmethod
    def from_private_bytes(cls, data: bytes) -> KeyPair:
        from cryptography.hazmat.primitives.serialization import load_der_private_key

        private = load_der_private_key(data, password=None)
        if not isinstance(private, Ed25519PrivateKey):
            raise TypeError("Expected Ed25519 private key")
        return cls(private_key=private, public_key=private.public_key())

    @classmethod
    def from_public_bytes(cls, data: bytes) -> KeyPair:
        from cryptography.hazmat.primitives.serialization import load_der_public_key

        public = load_der_public_key(data)
        if not isinstance(public, Ed25519PublicKey):
            raise TypeError("Expected Ed25519 public key")
        return cls(private_key=None, public_key=public)

    @classmethod
    def load(cls, private_path: Path, public_path: Path) -> KeyPair:
        private_bytes = private_path.read_bytes()
        public_path.read_bytes()
        from cryptography.hazmat.primitives.serialization import (
            load_der_private_key,
        )

        private = load_der_private_key(private_bytes, password=None)
        if not isinstance(private, Ed25519PrivateKey):
            raise TypeError("Expected Ed25519 private key")
        return cls(private_key=private, public_key=private.public_key())

    def can_sign(self) -> bool:
        """Check if this key pair has a private key for signing."""
        return self._private_key is not None

    def sign_data(self, data: bytes) -> bytes:
        """Sign data using the private key."""
        if self._private_key is None:
            raise ValueError("No private key available for signing")
        return self._private_key.sign(data)

    def verify_data(self, signature: bytes, data: bytes) -> None:
        """Verify a signature. Raises InvalidSignature on failure."""
        self._public_key.verify(signature, data)

    @property
    def private_key_bytes(self) -> bytes:
        if self._private_key is None:
            raise ValueError("No private key available")
        return self._private_key.private_bytes(Encoding.DER, PrivateFormat.PKCS8, NoEncryption())

    @property
    def public_key_bytes(self) -> bytes:
        return self._public_key.public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)

    def save(self, private_path: Path, public_path: Path) -> None:
        private_path.write_bytes(self.private_key_bytes)
        public_path.write_bytes(self.public_key_bytes)


class CartridgeSigner:
    """Sign and verify cartridge data using Ed25519."""

    def __init__(self, keypair: KeyPair) -> None:
        self._keypair = keypair

    @classmethod
    def from_public_bytes(cls, public_bytes: bytes) -> CartridgeSigner:
        kp = KeyPair.from_public_bytes(public_bytes)
        return cls(kp)

    def sign(self, data: bytes) -> bytes:
        return self._keypair.sign_data(data)

    def verify(self, data: bytes, signature: bytes) -> bool:
        try:
            self._keypair.verify_data(signature, data)
            return True
        except InvalidSignature:
            return False

    def sign_file(self, path: Path) -> bytes:
        return self.sign(path.read_bytes())

    def verify_file(self, path: Path, signature: bytes) -> bool:
        return self.verify(path.read_bytes(), signature)
