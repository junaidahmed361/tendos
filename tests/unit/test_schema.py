"""Tests for cartridge schema validation — written BEFORE implementation (TDD)."""

from __future__ import annotations

import pytest

from tendos.cartridge.schema import (
    AgentConfig,
    AgentNode,
    CartridgeManifest,
    ComposabilityConfig,
    HardwareRequirements,
    InferenceParams,
    LoRAAdapter,
    MemoryConfig,
    ModelConfig,
    PricingConfig,
    PricingModel,
    ToolDefinition,
)


class TestPricingModel:
    def test_free_model(self):
        p = PricingConfig(model=PricingModel.FREE)
        assert p.model == PricingModel.FREE
        assert p.price_per_call is None

    def test_pay_per_use_requires_price(self):
        p = PricingConfig(model=PricingModel.PAY_PER_USE, price_per_call=0.02)
        assert p.price_per_call == 0.02

    def test_pay_per_use_without_price_raises(self):
        with pytest.raises(ValueError, match="price_per_call"):
            PricingConfig(model=PricingModel.PAY_PER_USE)


class TestLoRAAdapter:
    def test_valid_adapter(self):
        a = LoRAAdapter(path="loras/clinical.safetensors", checksum="sha256:abc123")
        assert a.path == "loras/clinical.safetensors"
        assert a.checksum.startswith("sha256:")

    def test_checksum_must_have_prefix(self):
        with pytest.raises(ValueError, match="prefix"):
            LoRAAdapter(path="loras/x.safetensors", checksum="abc123")


class TestInferenceParams:
    def test_defaults(self):
        p = InferenceParams()
        assert p.temperature == 0.7
        assert p.max_tokens == 4096
        assert p.top_p == 0.9

    def test_temperature_bounds(self):
        with pytest.raises(ValueError, match="temperature"):
            InferenceParams(temperature=3.0)
        with pytest.raises(ValueError, match="temperature"):
            InferenceParams(temperature=-0.1)


class TestModelConfig:
    def test_minimal_config(self):
        m = ModelConfig(base="llama-3.3-70b-q4", source="ollama")
        assert m.base == "llama-3.3-70b-q4"
        assert m.loras == []
        assert m.fallback is None

    def test_with_loras_and_fallback(self):
        m = ModelConfig(
            base="llama-3.3-70b-q4",
            source="ollama",
            loras=[LoRAAdapter(path="loras/x.safetensors", checksum="sha256:abc")],
            fallback="gpt-4o",
        )
        assert len(m.loras) == 1
        assert m.fallback == "gpt-4o"


class TestAgentConfig:
    def test_minimal_agent(self):
        a = AgentConfig(system_prompt="prompts/system.txt")
        assert a.nodes == []
        assert a.tools == []

    def test_full_agent(self):
        a = AgentConfig(
            system_prompt="prompts/system.jinja2",
            nodes=[AgentNode(name="router", role="planner")],
            tools=[
                ToolDefinition(name="fhir_api", protocol="mcp", definition_path="tools/fhir.json")
            ],
            dag_path="graphs/workflow.yaml",
            memory=MemoryConfig(vector_db="chroma", embeddings_model="nomic-embed-text"),
        )
        assert len(a.nodes) == 1
        assert a.tools[0].protocol == "mcp"
        assert a.memory is not None
        assert a.memory.vector_db == "chroma"


class TestComposabilityConfig:
    def test_empty_composability(self):
        c = ComposabilityConfig()
        assert c.depends_on == []
        assert c.stacks_with == []
        assert c.conflicts_with == []

    def test_with_dependencies(self):
        c = ComposabilityConfig(
            depends_on=["hub://base-runtime"],
            stacks_with=["billing-coder-v1"],
            conflicts_with=["legacy-coder-v0"],
        )
        assert len(c.depends_on) == 1


class TestHardwareRequirements:
    def test_defaults(self):
        h = HardwareRequirements()
        assert h.requires_gpu is False
        assert h.min_vram_gb is None

    def test_gpu_required(self):
        h = HardwareRequirements(requires_gpu=True, min_vram_gb=8)
        assert h.min_vram_gb == 8


class TestCartridgeManifest:
    @pytest.fixture
    def minimal_manifest_data(self):
        return {
            "name": "test-cartridge",
            "version": "1.0.0",
            "author": "testuser",
            "domain": "healthcare",
            "description": "A test cartridge",
            "license": "Apache-2.0",
            "model": {"base": "llama-3.3-70b-q4", "source": "ollama"},
            "agent": {"system_prompt": "prompts/system.txt"},
        }

    def test_minimal_manifest(self, minimal_manifest_data):
        m = CartridgeManifest(**minimal_manifest_data)
        assert m.name == "test-cartridge"
        assert m.version == "1.0.0"
        assert m.pricing.model == PricingModel.FREE

    def test_version_must_be_semver(self):
        with pytest.raises(ValueError, match="[Ss]emantic|[Vv]ersion"):
            CartridgeManifest(
                name="x",
                version="not-semver",
                author="a",
                domain="test",
                description="d",
                license="Apache-2.0",
                model=ModelConfig(base="x", source="ollama"),
                agent=AgentConfig(system_prompt="p.txt"),
            )

    def test_name_validation(self):
        """Names must be lowercase alphanumeric with hyphens only."""
        with pytest.raises(ValueError, match="[Nn]ame|lowercase"):
            CartridgeManifest(
                name="Invalid Name!",
                version="1.0.0",
                author="a",
                domain="test",
                description="d",
                license="Apache-2.0",
                model=ModelConfig(base="x", source="ollama"),
                agent=AgentConfig(system_prompt="p.txt"),
            )

    def test_full_manifest(self, minimal_manifest_data):
        data = {
            **minimal_manifest_data,
            "tags": ["ICD-10", "FHIR"],
            "pricing": {"model": "pay_per_use", "price_per_call": 0.02},
            "hardware": {"requires_gpu": True, "min_vram_gb": 8},
            "privacy": {"data_stays_local": True, "compliance_attestations": ["HIPAA"]},
            "composability": {"depends_on": ["hub://base-runtime"]},
            "evaluation": {"accuracy_score": 0.94, "latency_p50_ms": 420, "dataset": "MIMIC-III"},
        }
        m = CartridgeManifest(**data)
        assert m.pricing.price_per_call == 0.02
        assert m.hardware.requires_gpu is True
        assert "HIPAA" in m.privacy.compliance_attestations

    def test_to_json_roundtrip(self, minimal_manifest_data):
        m = CartridgeManifest(**minimal_manifest_data)
        json_str = m.model_dump_json(indent=2)
        m2 = CartridgeManifest.model_validate_json(json_str)
        assert m == m2
