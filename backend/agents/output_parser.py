import json
from typing import Optional, Type, TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class OutputParser:
    """
    Centralized parser for LLM outputs.
    Strips markdown code fences, validates JSON against Pydantic schemas, and normalizes responses.
    """

    @staticmethod
    def strip_code_fences(text: str) -> str:
        """Strips ```json or ``` markdown code blocks from raw LLM text."""
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]

        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

        return cleaned.strip()

    @classmethod
    def parse_json(cls, text: str, model_cls: Type[T]) -> Optional[T]:
        """
        Strips code fences, parses JSON, and validates against the provided Pydantic model class.
        Returns instance of T on success, or None on failure.
        """
        if not text:
            return None

        cleaned_text = cls.strip_code_fences(text)
        try:
            return model_cls.model_validate_json(cleaned_text)
        except (ValidationError, json.JSONDecodeError):
            return None
