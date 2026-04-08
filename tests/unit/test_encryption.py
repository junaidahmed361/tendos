"""Tests for LoRA weight encryption — TDD."""

from __future__ import annotations

import pytest

from tendos.security.encryption import WeightEncryptor


class TestWeightEncryptor:
    def test_generate_key(self):
        key = WeightEncryptor.generate_key()
        assert isinstance(key, bytes)
        assert len(key) == 32  # AES-256

    def test_encrypt_decrypt_roundtrip(self):
        key = WeightEncryptor.generate_key()
        enc = WeightEncryptor(key)
        plaintext = b"These are LoRA weight bytes " * 100
        ciphertext = enc.encrypt(plaintext)
        assert ciphertext != plaintext
        decrypted = enc.decrypt(ciphertext)
        assert decrypted == plaintext

    def test_decrypt_with_wrong_key_fails(self):
        key1 = WeightEncryptor.generate_key()
        key2 = WeightEncryptor.generate_key()
        enc1 = WeightEncryptor(key1)
        enc2 = WeightEncryptor(key2)
        ciphertext = enc1.encrypt(b"secret weights")
        with pytest.raises(Exception):  # noqa: B017, PT011
            enc2.decrypt(ciphertext)

    def test_encrypt_file_roundtrip(self, tmp_path):
        key = WeightEncryptor.generate_key()
        enc = WeightEncryptor(key)
        original = b"weight data " * 500
        input_file = tmp_path / "weights.safetensors"
        input_file.write_bytes(original)
        encrypted_file = tmp_path / "weights.safetensors.enc"
        enc.encrypt_file(input_file, encrypted_file)
        assert encrypted_file.exists()
        assert encrypted_file.read_bytes() != original
        output_file = tmp_path / "weights_decrypted.safetensors"
        enc.decrypt_file(encrypted_file, output_file)
        assert output_file.read_bytes() == original

    def test_ciphertext_includes_nonce(self):
        key = WeightEncryptor.generate_key()
        enc = WeightEncryptor(key)
        ct1 = enc.encrypt(b"same data")
        ct2 = enc.encrypt(b"same data")
        assert ct1 != ct2  # Different nonces each time
