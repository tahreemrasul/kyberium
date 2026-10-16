import io
from collections.abc import Callable
from typing import Any

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.ai.client import AIError
from app.config import Settings
from app.demo import sample_garments
from app.deps import ai_dep, blobs_dep, repo_dep, retriever_dep, settings_dep
from app.knowledge import NoOpFashionKnowledgeRetriever
from app.main import app
from app.schemas import Garment
from app.storage.blobs import LocalBlobStore
from app.storage.repository import LocalRepository


class FakeAI:
    """Stands in for GeminiClient. `responses` maps schema class name -> value | Exception | callable."""

    def __init__(self, responses: dict[str, Any] | None = None, settings: Settings | None = None) -> None:
        self.responses = responses or {}
        self.settings = settings or Settings(ai_backend="vertex", google_cloud_project="test-project")
        self.calls: list[dict] = []

    def image_part(self, data: bytes, mime_type: str) -> str:
        return f"<image {len(data)} bytes>"

    async def generate_json(self, *, schema, contents, system, **kw):
        self.calls.append({"schema": schema.__name__, "contents": contents, **kw})
        r = self.responses.get(schema.__name__)
        if r is None:
            raise AIError("ai_upstream_error", "no fake response configured", retryable=True)
        if isinstance(r, Exception):
            raise r
        if callable(r):
            r = r(contents)
        return schema.model_validate(r) if isinstance(r, dict) else r


@pytest.fixture
def settings(tmp_path) -> Settings:
    return Settings(ai_backend="off", local_data_dir=tmp_path, fashion_knowledge_backend="none")


@pytest.fixture
def client(tmp_path, settings) -> TestClient:
    repo = LocalRepository(tmp_path / "owners")
    blobs = LocalBlobStore(tmp_path / "blobs")
    state: dict[str, Any] = {"ai": None}
    app.dependency_overrides.update(
        {
            repo_dep: lambda: repo,
            blobs_dep: lambda: blobs,
            ai_dep: lambda: state["ai"],
            retriever_dep: lambda: NoOpFashionKnowledgeRetriever(),
            settings_dep: lambda: settings,
        }
    )
    c = TestClient(app)
    c.state = state  # tests may set c.state["ai"] = FakeAI(...)
    c.repo = repo
    yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth(client) -> Callable[[], dict[str, str]]:
    def make() -> dict[str, str]:
        token = client.post("/session").json()["token"]
        return {"Authorization": f"Bearer {token}"}

    return make


@pytest.fixture
def wardrobe() -> dict[str, Garment]:
    return {g.id: g for g in sample_garments()}


def image_bytes(fmt: str = "PNG", size=(64, 80), color=(150, 170, 140)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, format=fmt)
    return buf.getvalue()
