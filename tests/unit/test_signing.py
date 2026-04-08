"""Tests for cartridge signing and verification — TDD."""

from __future__ import annotations

import pytest

from tendos.security.signing import CartridgeSigner, KeyPair


class TestKeyPair:
    def test_generate_keypair(self):
        kp = KeyPair.generate()
        assert kp.private_key_bytes is not None
        assert kp.public_key_bytes is not None
        assert len(kp.private_key_bytes) > 0
        assert len(kp.public_key_bytes) > 0

    def test_keypair_deterministic_public_key(self):
        kp = KeyPair.generate()
        kp2 = KeyPair.from_private_bytes(kp.private_key_bytes)
        assert kp.public_key_bytes == kp2.public_key_bytes

    def test_save_and_load_keypair(self, tmp_path):
        kp = KeyPair.generate()
        private_path = tmp_path / "test.key"
        public_path = tmp_path / "test.pub"
        kp.save(private_path, public_path)
        loaded = KeyPair.load(private_path, public_path)
        assert loaded.private_key_bytes == kp.private_key_bytes
        assert loaded.public_key_bytes == kp.public_key_bytes


class TestCartridgeSigner:
    @pytest.fixture
    def keypair(self):
        return KeyPair.generate()

    @pytest.fixture
    def signer(self, keypair):
        return CartridgeSigner(keypair)

    def test_sign_bytes(self, signer):
        data = b"hello world"
        sig = signer.sign(data)
        assert isinstance(sig, bytes)
        assert len(sig) == 64  # Ed25519 signature length

    def test_verify_valid_signature(self, signer):
        data = b"test data"
        sig = signer.sign(data)
        assert signer.verify(data, sig) is True

    def test_verify_invalid_signature(self, signer):
        data = b"test data"
        bad_sig = b"\x00" * 64
        assert signer.verify(data, bad_sig) is False

    def test_verify_tampered_data(self, signer):
        data = b"original"
        sig = signer.sign(data)
        assert signer.verify(b"tampered", sig) is False

    def test_sign_file(self, signer, tmp_path):
        test_file = tmp_path / "test.bin"
        test_file.write_bytes(b"file content for signing")
        sig = signer.sign_file(test_file)
        assert signer.verify_file(test_file, sig) is True

    def test_verify_with_public_key_only(self, keypair):
        signer = CartridgeSigner(keypair)
        data = b"signed data"
        sig = signer.sign(data)
        # Create verifier with only public key
        verifier = CartridgeSigner.from_public_bytes(keypair.public_key_bytes)
        assert verifier.verify(data, sig) is True
