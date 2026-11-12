"""Load and validate the bundled model context-window registry."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List


PROVIDERS = (
    "Anthropic",
    "OpenAI",
    "Google",
    "xAI",
    "Meta",
    "DeepSeek",
    "Mistral",
)


@dataclass(frozen=True)
class ModelRecord:
    """Context-window metadata for one curated model."""

    provider: str
    model_id: str
    display_name: str
    max_input_tokens: int
    max_output_tokens: int


def load_model_registry() -> List[ModelRecord]:
    """Return validated model records from the package's bundled JSON file."""
    # Resolve next to this file rather than by package name, so the registry
    # loads when token_counter.py is run as a plain script.
    registry_path = Path(__file__).with_name("model_registry.json")
    with registry_path.open(encoding="utf-8") as registry_file:
        payload = json.load(registry_file)

    raw_models = payload.get("models") if isinstance(payload, dict) else None
    if not isinstance(raw_models, list) or not raw_models:
        raise ValueError("Model registry must contain a non-empty 'models' list")

    records = []
    seen_ids = set()
    required_fields = {
        "provider",
        "model_id",
        "display_name",
        "max_input_tokens",
        "max_output_tokens",
    }

    for index, raw_model in enumerate(raw_models):
        if not isinstance(raw_model, dict):
            raise ValueError(f"Model registry entry {index} must be an object")

        missing_fields = required_fields - raw_model.keys()
        if missing_fields:
            missing = ", ".join(sorted(missing_fields))
            raise ValueError(f"Model registry entry {index} is missing: {missing}")

        provider = raw_model["provider"]
        model_id = raw_model["model_id"]
        display_name = raw_model["display_name"]
        max_input_tokens = raw_model["max_input_tokens"]
        max_output_tokens = raw_model["max_output_tokens"]

        if provider not in PROVIDERS:
            raise ValueError(f"Unknown model provider: {provider!r}")
        if not isinstance(model_id, str) or not model_id.strip():
            raise ValueError(f"Model registry entry {index} has an invalid model_id")
        if model_id in seen_ids:
            raise ValueError(f"Duplicate model ID in registry: {model_id}")
        if not isinstance(display_name, str) or not display_name.strip():
            raise ValueError(f"Model {model_id!r} has an invalid display_name")
        for field_name, value in (
            ("max_input_tokens", max_input_tokens),
            ("max_output_tokens", max_output_tokens),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"Model {model_id!r} has an invalid {field_name}")

        seen_ids.add(model_id)
        records.append(
            ModelRecord(
                provider=provider,
                model_id=model_id,
                display_name=display_name,
                max_input_tokens=max_input_tokens,
                max_output_tokens=max_output_tokens,
            )
        )

    return records
