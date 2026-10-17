import logging
from time import perf_counter
from typing import Any

from pydantic import ValidationError

from config_loader import MappingRule, ParameterRule
from schema import RawPayload, UnifiedContext

logger = logging.getLogger(__name__)


class TranslationEngine:
    version = "1.0"

    @property
    def status(self) -> str:
        return "ready"

    def transform(
        self, payload: RawPayload, mapping_rules: MappingRule
    ) -> UnifiedContext:
        started = perf_counter()
        try:
            parameters: dict[str, Any] = {}
            for target, rule in mapping_rules.parameters.items():
                parameter_rule = rule if isinstance(rule, ParameterRule) else (
                    ParameterRule(path=rule)
                    if isinstance(rule, str)
                    else ParameterRule.model_validate(rule)
                )
                value = self._read_path(payload.data, parameter_rule.path)
                parameters[target] = self._transform_value(value, parameter_rule)

            result = UnifiedContext(
                source=mapping_rules.source,
                action=mapping_rules.action,
                parameters=parameters,
                meta={"status": "ok", "version": self.version},
            )
        except (KeyError, TypeError, ValueError, OverflowError, ValidationError) as exc:
            logger.warning(
                "Mapping failed for source %r: %s",
                payload.source_id,
                exc,
                exc_info=True,
            )
            result = UnifiedContext(
                source=payload.source_id,
                action=payload.payload_type,
                parameters={},
                meta={"status": "error", "error": str(exc), "version": self.version},
            )

        result.meta["processing_time_ms"] = (perf_counter() - started) * 1000
        return result

    @staticmethod
    def _read_path(data: dict[str, Any], path: str) -> Any:
        value: Any = data
        for part in path.split("."):
            if not isinstance(value, dict):
                raise TypeError(f"Cannot traverse mapping path: {path}")
            value = value[part]
        return value

    @staticmethod
    def _transform_value(value: Any, rule: ParameterRule) -> Any:
        if rule.cast == "str":
            value = str(value)
        elif rule.cast == "int":
            value = int(value)
        elif rule.cast == "float":
            value = float(value)
        elif rule.cast == "bool":
            value = TranslationEngine._cast_bool(value)

        if rule.multiply is not None or rule.add is not None:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError("Arithmetic transformations require a numeric value")
            value = value * (rule.multiply if rule.multiply is not None else 1)
            value += rule.add if rule.add is not None else 0

        if rule.format is not None:
            if rule.format == "uppercase":
                if not isinstance(value, str):
                    raise TypeError("uppercase formatting requires a string value")
                value = value.upper()
            elif rule.format == "lowercase":
                if not isinstance(value, str):
                    raise TypeError("lowercase formatting requires a string value")
                value = value.lower()
            else:
                value = format(value, rule.format)

        if rule.unit is not None:
            value = f"{value} {rule.unit}"
        return value

    @staticmethod
    def _cast_bool(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)) and value in (0, 1):
            return bool(value)
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"true", "yes", "1"}:
                return True
            if normalized in {"false", "no", "0"}:
                return False
        raise ValueError(f"Cannot cast {value!r} to bool")
