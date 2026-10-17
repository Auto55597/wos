import json
import os
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, ValidationError, field_validator


class ConfigurationError(Exception):
    """Raised when external mapping configuration is unavailable or invalid."""


class ParameterRule(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    path: str
    cast: Literal["str", "int", "float", "bool"] | None = None
    format: str | None = None
    multiply: int | float | None = None
    add: int | float | None = None
    unit: str | None = None

    @field_validator("path")
    @classmethod
    def validate_path(cls, path: str) -> str:
        if not path or any(not part for part in path.split(".")):
            raise ValueError("Mapping paths must contain non-empty dot-separated keys")
        return path


class MappingRule(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    source: str
    action: str
    parameters: dict[str, str | ParameterRule]

    @field_validator("parameters")
    @classmethod
    def validate_parameter_rules(
        cls, rules: dict[str, str | ParameterRule]
    ) -> dict[str, str | ParameterRule]:
        for rule in rules.values():
            if isinstance(rule, str):
                ParameterRule(path=rule)
        return rules


def load_mapping_rules(
    path: str | Path | None = None,
) -> dict[str, MappingRule]:
    configured_path = path if path is not None else os.getenv("WOS_MAPPING_FILE")
    if configured_path is None or not str(configured_path).strip():
        raise ConfigurationError("Set WOS_MAPPING_FILE to a JSON mapping configuration")

    config_path = Path(configured_path)
    try:
        with config_path.open(encoding="utf-8") as config_file:
            raw_rules: Any = json.load(config_file)
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigurationError(
            f"Unable to load mapping configuration '{config_path}': {exc}"
        ) from exc

    if not isinstance(raw_rules, dict) or not raw_rules:
        raise ConfigurationError("Mapping configuration must be a non-empty JSON object")

    rules: dict[str, MappingRule] = {}
    for rule_id, rule_data in raw_rules.items():
        if not isinstance(rule_id, str) or not rule_id.strip():
            raise ConfigurationError("Mapping rule identifiers must be non-empty strings")
        try:
            rules[rule_id] = MappingRule.model_validate(rule_data)
        except ValidationError as exc:
            raise ConfigurationError(f"Invalid mapping rule '{rule_id}': {exc}") from exc

    return rules
