from __future__ import annotations

import json
import re
from typing import Any, Optional, Type, TypeVar

from google import genai
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class GeminiJSONClient:
    """Small wrapper around Gemini for grounded JSON responses.

    It deliberately keeps the API surface tiny:
    - one method for section drafts
    - one method for final briefing JSON

    """

    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def generate_json(
        self,
        *,
        model: str,
        prompt: str,
        schema_model: Type[T],
        use_search: bool,
        max_output_tokens: Optional[int],
        temperature: float = 0.35,
    ) -> T:
        tools = [{"google_search": {}}, {"url_context": {}}] if use_search else []

        schema = schema_model.model_json_schema()
        config_main: dict[str, Any] = {
            "temperature": temperature,
            "response_mime_type": "application/json",
            "response_schema": schema_model,
        }
        if max_output_tokens is not None:
            config_main["max_output_tokens"] = max_output_tokens
        if tools:
            config_main["tools"] = tools

        try:
            response = self.client.models.generate_content(
                model=model,
                contents=prompt,
                config=config_main,
            )
            return self._parse_response(response.text, schema_model)
        except Exception as first_error:
            config_fallback: dict[str, Any] = {
                "temperature": temperature,
                "response_mime_type": "application/json",
                "response_json_schema": schema,
            }
            if max_output_tokens is not None:
                config_fallback["max_output_tokens"] = max_output_tokens
            if tools:
                config_fallback["tools"] = tools

            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=config_fallback,
                )
                return self._parse_response(response.text, schema_model)
            except Exception as second_error:
                raise RuntimeError(
                    "Gemini JSON generation failed with both structured-output config styles.\n"
                    f"First error: {first_error}\nSecond error: {second_error}"
                ) from second_error

    @staticmethod
    def _parse_response(text: str, schema_model: Type[T]) -> T:
        cleaned = _extract_json(text)
        try:
            return schema_model.model_validate_json(cleaned)
        except ValidationError:
            # Some models return valid JSON but with whitespace/code fences oddities.
            data = json.loads(cleaned)
            return schema_model.model_validate(data)


def _extract_json(text: str) -> str:
    """Extract JSON from a raw model response, tolerating fenced code blocks."""
    text = text.strip()
    if text.startswith("```"):
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.DOTALL | re.IGNORECASE)
        if match:
            text = match.group(1).strip()

    # If the model adds a sentence before/after JSON, take the outer JSON object.
    first = text.find("{")
    last = text.rfind("}")
    if first != -1 and last != -1 and last > first:
        return text[first : last + 1]
    return text
