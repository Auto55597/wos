from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RawPayload(BaseModel):
    model_config = ConfigDict(strict=True)

    source_id: str
    payload_type: str
    data: dict[str, Any]
    timestamp: float | None = None


class UnifiedContext(BaseModel):
    model_config = ConfigDict(strict=True)

    context_id: str = Field(default_factory=lambda: str(uuid4()))
    source: str
    action: str
    parameters: dict[str, Any]
    meta: dict[str, Any] = Field(default_factory=dict)

    @field_validator("context_id")
    @classmethod
    def validate_context_id(cls, value: str) -> str:
        UUID(value)
        return value
