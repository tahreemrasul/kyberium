"""Thin, defensive wrapper around the Google Gen AI SDK (Vertex AI mode).

Responsibilities: structured JSON output validated by Pydantic, bounded
timeouts, limited retries with backoff on transient errors, one repair attempt
for malformed output, and latency/token logging. It never fabricates a result:
callers get a validated model instance or an ``AIError``.
"""

import asyncio
import copy
import json
import logging
import random
import time
from functools import lru_cache
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from app.config import Settings, get_settings

log = logging.getLogger("rewear.ai")
T = TypeVar("T", bound=BaseModel)

_TRANSIENT = {408, 429, 500, 502, 503, 504}


class AIError(Exception):
    def __init__(self, code: str, message: str, *, retryable: bool = False) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.retryable = retryable


class AIUnavailable(AIError):
    def __init__(self) -> None:
        super().__init__("ai_unavailable", "Gemini is not configured for this deployment.", retryable=False)


def inline_schema(model: type[BaseModel]) -> dict[str, Any]:
    """JSON schema with $refs inlined and noise removed, for response_json_schema."""
    schema = model.model_json_schema()
    defs = schema.pop("$defs", {})

    def walk(node: Any) -> Any:
        if isinstance(node, dict):
            if "$ref" in node:
                return walk(copy.deepcopy(defs[node["$ref"].split("/")[-1]]))
            # Drop "title"/"default" annotations (scalars/lists), but keep properties that happen to be
            # named "title" — those are sub-schemas (dicts).
            return {k: walk(v) for k, v in node.items() if k not in ("title", "default") or isinstance(v, dict)}
        if isinstance(node, list):
            return [walk(v) for v in node]
        return node

    return walk(schema)


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text
        text = text.rsplit("```", 1)[0]
    return text.strip()


class GeminiClient:
    def __init__(self, settings: Settings) -> None:
        from google import genai
        from google.genai import types

        self._types = types
        self.settings = settings
        self._client = genai.Client(
            vertexai=True,
            project=settings.google_cloud_project,
            location=settings.google_cloud_location,
            http_options=types.HttpOptions(timeout=int(settings.gemini_timeout_s * 1000)),
        )

    def image_part(self, data: bytes, mime_type: str):
        return self._types.Part.from_bytes(data=data, mime_type=mime_type)

    async def generate_json(
        self,
        *,
        schema: type[T],
        contents: list[Any],
        system: str,
        model: str | None = None,
        temperature: float = 0.4,
        thinking_budget: int | None = None,
        label: str = "gemini",
    ) -> T:
        types = self._types
        model = model or self.settings.gemini_model
        json_schema = inline_schema(schema)
        use_schema_param = True
        repair_note: str | None = None
        last_error: AIError | None = None
        attempts = self.settings.gemini_max_retries + 1

        for attempt in range(attempts):
            parts = list(contents)
            sys_text = system
            if not use_schema_param:
                sys_text += "\n\nReturn ONLY JSON matching this JSON schema:\n" + json.dumps(json_schema)
            if repair_note:
                parts.append(repair_note)
            cfg: dict[str, Any] = {
                "system_instruction": sys_text,
                "temperature": temperature,
                "response_mime_type": "application/json",
            }
            if use_schema_param:
                cfg["response_json_schema"] = json_schema
            if thinking_budget is not None and model.startswith("gemini-2.5"):
                cfg["thinking_config"] = types.ThinkingConfig(thinking_budget=thinking_budget)

            started = time.perf_counter()
            try:
                resp = await asyncio.wait_for(
                    self._client.aio.models.generate_content(
                        model=model, contents=parts, config=types.GenerateContentConfig(**cfg)
                    ),
                    timeout=self.settings.gemini_timeout_s + 5,
                )
            except TimeoutError:
                last_error = AIError("ai_timeout", "The AI stylist took too long to respond.", retryable=True)
                log.warning("%s timeout attempt=%d", label, attempt + 1)
                await self._backoff(attempt)
                continue
            except Exception as exc:  # google.genai.errors.APIError and transport errors
                status = getattr(exc, "code", None)
                msg = str(exc)
                log.warning("%s error attempt=%d status=%s %s", label, attempt + 1, status, msg[:300])
                if status == 400 and use_schema_param and "schema" in msg.lower():
                    use_schema_param = False  # retry with the schema in the prompt instead
                    continue
                if status in _TRANSIENT or status is None:
                    code = "ai_rate_limited" if status == 429 else "ai_upstream_error"
                    last_error = AIError(code, "The AI service is temporarily unavailable.", retryable=True)
                    await self._backoff(attempt)
                    continue
                raise AIError("ai_request_rejected", f"The AI service rejected the request ({status}).") from exc

            latency_ms = int((time.perf_counter() - started) * 1000)
            usage = getattr(resp, "usage_metadata", None)
            log.info(
                "%s ok model=%s attempt=%d latency_ms=%d in_tokens=%s out_tokens=%s",
                label,
                model,
                attempt + 1,
                latency_ms,
                getattr(usage, "prompt_token_count", None),
                getattr(usage, "candidates_token_count", None),
            )
            text = getattr(resp, "text", None) or ""
            try:
                return schema.model_validate_json(_strip_fences(text))
            except (ValidationError, ValueError) as exc:
                err = str(exc)[:800]
                log.warning("%s malformed output attempt=%d: %s", label, attempt + 1, err[:300])
                last_error = AIError("ai_malformed_output", "The AI returned an unusable answer.", retryable=True)
                repair_note = (
                    "Your previous answer was not valid for the required schema. Error: "
                    f"{err}\nReturn only corrected JSON."
                )
                continue

        raise last_error or AIError("ai_upstream_error", "The AI service failed.", retryable=True)

    async def _backoff(self, attempt: int) -> None:
        if attempt + 1 < self.settings.gemini_max_retries + 1:
            await asyncio.sleep(min(8.0, 1.2 * 2**attempt) + random.random() * 0.4)


@lru_cache
def _cached_client() -> GeminiClient:
    return GeminiClient(get_settings())


def get_ai() -> GeminiClient | None:
    """Return the shared client, or None when AI is disabled (demo mode)."""
    s = get_settings()
    if not s.ai_enabled:
        return None
    return _cached_client()
