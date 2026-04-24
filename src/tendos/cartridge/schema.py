"""Cartridge manifest schema — Pydantic v2 models for cartridge validation."""

from __future__ import annotations

import re
from enum import Enum
from typing import Any

from pydantic import BaseModel, field_validator, model_validator


class PricingModel(str, Enum):
    """Pricing model types for cartridges."""

    FREE = "free"
    PAY_PER_USE = "pay_per_use"
    SUBSCRIPTION = "subscription"


class PricingConfig(BaseModel):
    """Pricing configuration for a cartridge."""

    model: PricingModel = PricingModel.FREE
    price_per_call: float | None = None

    @model_validator(mode="after")
    def validate_pay_per_use_has_price(self) -> PricingConfig:
        """PAY_PER_USE model requires a price_per_call."""
        if self.model == PricingModel.PAY_PER_USE and self.price_per_call is None:
            raise ValueError("PAY_PER_USE pricing requires price_per_call to be set")
        return self


class LoRAAdapter(BaseModel):
    """LoRA adapter configuration for model fine-tuning."""

    path: str
    checksum: str

    @field_validator("checksum")
    @classmethod
    def validate_checksum_format(cls, v: str) -> str:
        """Checksum must be prefixed with algorithm (e.g., 'sha256:')."""
        if ":" not in v:
            raise ValueError("Checksum must include algorithm prefix (e.g., 'sha256:abc123')")
        return v


class InferenceParams(BaseModel):
    """Inference parameters for model generation."""

    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 0.9

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        """Temperature must be between 0 and 2."""
        if not (0 <= v <= 2):
            raise ValueError("temperature must be between 0 and 2")
        return v

    @field_validator("max_tokens")
    @classmethod
    def validate_max_tokens(cls, v: int) -> int:
        """max_tokens must be positive."""
        if v <= 0:
            raise ValueError("max_tokens must be greater than 0")
        return v

    @field_validator("top_p")
    @classmethod
    def validate_top_p(cls, v: float) -> float:
        """top_p must be between 0 and 1."""
        if not (0 <= v <= 1):
            raise ValueError("top_p must be between 0 and 1")
        return v


class ModelConfig(BaseModel):
    """Model configuration for the cartridge."""

    base: str
    source: str
    loras: list[LoRAAdapter] = []
    fallback: str | None = None
    inference_params: InferenceParams = InferenceParams()


class AgentNode(BaseModel):
    """Agent node in the cartridge workflow."""

    name: str
    role: str
    description: str = ""


class ToolDefinition(BaseModel):
    """Tool definition for agent use."""

    name: str
    protocol: str = "mcp"
    definition_path: str


class MemoryConfig(BaseModel):
    """Memory and retrieval configuration."""

    vector_db: str
    embeddings_model: str


class AgentConfig(BaseModel):
    """Agent configuration for the cartridge."""

    system_prompt: str
    nodes: list[AgentNode] = []
    tools: list[ToolDefinition] = []
    dag_path: str | None = None
    memory: MemoryConfig | None = None


class ComposabilityConfig(BaseModel):
    """Composability configuration for cartridge dependencies."""

    depends_on: list[str] = []
    stacks_with: list[str] = []
    conflicts_with: list[str] = []


class EvaluationMetadata(BaseModel):
    """Evaluation metrics and metadata."""

    accuracy_score: float | None = None
    latency_p50_ms: int | None = None
    dataset: str | None = None
    community_rating: float | None = None

    @field_validator("accuracy_score")
    @classmethod
    def validate_accuracy_score(cls, v: float | None) -> float | None:
        """Accuracy score must be between 0 and 1."""
        if v is not None and not (0 <= v <= 1):
            raise ValueError("accuracy_score must be between 0 and 1")
        return v

    @field_validator("community_rating")
    @classmethod
    def validate_community_rating(cls, v: float | None) -> float | None:
        """Community rating must be between 0 and 5."""
        if v is not None and not (0 <= v <= 5):
            raise ValueError("community_rating must be between 0 and 5")
        return v


class HardwareRequirements(BaseModel):
    """Hardware requirements for the cartridge."""

    requires_gpu: bool = False
    min_vram_gb: int | None = None


class PrivacyConfig(BaseModel):
    """Privacy and compliance configuration."""

    data_stays_local: bool = True
    compliance_attestations: list[str] = []


class PIIRedactionConfig(BaseModel):
    """PII redaction settings for harness execution."""

    enabled: bool = True
    strategy: str = "mask"
    entities: list[str] = []


class UpdateSyncConfig(BaseModel):
    """Update and sync policy for cartridge lifecycle."""

    strategy: str = "manual"
    interval: str | None = None
    signed_updates_required: bool = True


class HarnessDeclarations(BaseModel):
    """Harness declarations that can be defined in YAML or inline manifest."""

    security_guardrails: list[str] = []
    pii_redaction: PIIRedactionConfig | None = None
    update_sync: UpdateSyncConfig | None = None
    custom_config: dict[str, Any] = {}


class HarnessConfig(BaseModel):
    """Harness configuration with YAML path and optional inline declarations."""

    yaml_path: str | None = None
    declarations: HarnessDeclarations | None = None

    @model_validator(mode="after")
    def validate_harness_source(self) -> HarnessConfig:
        """Require either yaml_path or inline declarations."""
        if self.yaml_path is None and self.declarations is None:
            raise ValueError("harness requires yaml_path or declarations")
        return self


class CartridgeManifest(BaseModel):
    """Complete cartridge manifest specification."""

    name: str
    version: str
    author: str
    domain: str
    description: str
    license: str
    tags: list[str] = []
    pricing: PricingConfig = PricingConfig()
    model: ModelConfig
    agent: AgentConfig
    composability: ComposabilityConfig = ComposabilityConfig()
    evaluation: EvaluationMetadata = EvaluationMetadata()
    hardware: HardwareRequirements = HardwareRequirements()
    privacy: PrivacyConfig = PrivacyConfig()
    harness: HarnessConfig | None = None
    checksum: str | None = None
    signed: bool = False

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Version must be valid semantic versioning."""
        semver_pattern = r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?(\+[a-zA-Z0-9.]+)?$"
        if not re.match(semver_pattern, v):
            raise ValueError(f"version must be valid semantic version, got: {v}")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Name must be lowercase alphanumeric with hyphens (no leading/trailing hyphens)."""
        name_pattern = r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$"
        if not re.match(name_pattern, v):
            raise ValueError(f"name must be lowercase alphanumeric with hyphens, got: {v}")
        return v
