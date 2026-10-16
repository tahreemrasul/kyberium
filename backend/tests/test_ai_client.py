"""GeminiClient behaviour with a fake SDK transport: repair, retries, schema shaping."""

import json
from types import SimpleNamespace

import pytest

from app.ai.client import AIError, GeminiClient, inline_schema
from app.config import Settings
from app.schemas import CompositionResult, GarmentDraft

VALID = {"name": "Sage blazer", "category": "outerwear", "colors": ["sage"], "formality": "smart_casual"}


class FakeModels:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = 0

    async def generate_content(self, model, contents, config):
        self.calls += 1
        out = self.outcomes.pop(0)
        if isinstance(out, Exception):
            raise out
        return SimpleNamespace(text=out, usage_metadata=None)


async def _no_sleep(attempt):
    return None


def make_client(outcomes) -> tuple[GeminiClient, FakeModels]:
    from google.genai import types

    c = object.__new__(GeminiClient)
    c._types = types
    c.settings = Settings(ai_backend="vertex", google_cloud_project="p", gemini_max_retries=2, gemini_timeout_s=5)
    models = FakeModels(outcomes)
    c._client = SimpleNamespace(aio=SimpleNamespace(models=models))
    c._backoff = _no_sleep
    return c, models


class StatusError(Exception):
    def __init__(self, code, msg="err"):
        super().__init__(msg)
        self.code = code


async def test_valid_json_is_parsed():
    c, m = make_client([json.dumps(VALID)])
    draft = await c.generate_json(schema=GarmentDraft, contents=["x"], system="s")
    assert draft.category == "outerwear" and m.calls == 1


async def test_fenced_json_is_accepted():
    c, _ = make_client(["```json\n" + json.dumps(VALID) + "\n```"])
    assert (await c.generate_json(schema=GarmentDraft, contents=["x"], system="s")).name == "Sage blazer"


async def test_malformed_output_gets_repair_attempts():
    c, m = make_client(["{not json", json.dumps({**VALID, "category": "spaceship"}), json.dumps(VALID)])
    draft = await c.generate_json(schema=GarmentDraft, contents=["x"], system="s")
    assert draft.name == "Sage blazer" and m.calls == 3


async def test_persistent_malformed_output_raises():
    c, _ = make_client(["nope", "nope", "nope"])
    with pytest.raises(AIError) as exc:
        await c.generate_json(schema=GarmentDraft, contents=["x"], system="s")
    assert exc.value.code == "ai_malformed_output"


async def test_rate_limit_is_retried_then_surfaces():
    c, m = make_client([StatusError(429), StatusError(503), json.dumps(VALID)])
    assert (await c.generate_json(schema=GarmentDraft, contents=["x"], system="s")).name
    c, _ = make_client([StatusError(429)] * 3)
    with pytest.raises(AIError) as exc:
        await c.generate_json(schema=GarmentDraft, contents=["x"], system="s")
    assert exc.value.code == "ai_rate_limited" and exc.value.retryable


async def test_client_error_is_not_retried():
    c, m = make_client([StatusError(403, "permission denied")])
    with pytest.raises(AIError):
        await c.generate_json(schema=GarmentDraft, contents=["x"], system="s")
    assert m.calls == 1


def test_inline_schema_has_no_refs():
    s = json.dumps(inline_schema(CompositionResult))
    assert "$ref" not in s and "$defs" not in s
    assert "garment_id" in s
