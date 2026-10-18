"""Pluggable styling-knowledge retrieval.

Pipeline position: Inspiration analysis -> (optional) knowledge retrieval ->
wardrobe matching & outfit reasoning.

Knowledge hits are *principles* (e.g. "balance a boxy top with a defined
waist"). They are never garments and can never create owned items. Retrieval
is best-effort: ``safe_search`` swallows timeouts/errors and returns [] so the
wardrobe pipeline always runs.

To add a real vector index later, implement ``search`` in
``VectorFashionKnowledgeRetriever`` (pgvector, Qdrant, Vertex AI Vector Search…)
and set FASHION_KNOWLEDGE_BACKEND=vector. No endpoint or UI change is needed.
"""

import asyncio
import json
import logging
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Protocol

from pydantic import BaseModel, Field

from app.config import get_settings
from app.schemas import InspirationAnalysis, StylePreferences

log = logging.getLogger("rewear.knowledge")

DEFAULT_DATASET = Path(__file__).parent / "data" / "styling_principles.json"


class FashionKnowledgeQuery(BaseModel):
    concepts: list[str] = Field(default_factory=list)  # silhouette, proportion, layering, palette…
    occasion: str | None = None
    garment_categories: list[str] = Field(default_factory=list)
    style_tags: list[str] = Field(default_factory=list)
    text: str | None = None  # natural-language query for semantic backends


class FashionKnowledgeHit(BaseModel):
    id: str
    text: str
    score: float | None = None  # ranking value, not a probability of correctness
    tags: list[str] = Field(default_factory=list)
    source_title: str | None = None
    source_url: str | None = None
    license: str | None = None
    provenance: str | None = None


class FashionKnowledgeRetriever(Protocol):
    name: str

    async def search(
        self, query: FashionKnowledgeQuery, filters: dict[str, Any] | None = None, top_k: int = 4
    ) -> list[FashionKnowledgeHit]: ...


class NoOpFashionKnowledgeRetriever:
    name = "none"

    async def search(
        self, query: FashionKnowledgeQuery, filters: dict[str, Any] | None = None, top_k: int = 4
    ) -> list[FashionKnowledgeHit]:
        return []


_WORD = re.compile(r"[a-z]+")


def _terms(values: list[str]) -> set[str]:
    out: set[str] = set()
    for v in values:
        out.update(w for w in _WORD.findall(v.lower()) if len(w) > 2)
    return out


class LocalFashionKnowledgeRetriever:
    """Tag/keyword overlap over a small curated JSON dataset."""

    name = "local"

    def __init__(self, records: list[dict[str, Any]]) -> None:
        self._records = records

    @classmethod
    def from_path(cls, path: Path) -> "LocalFashionKnowledgeRetriever":
        return cls(json.loads(Path(path).read_text("utf-8")))

    async def search(
        self, query: FashionKnowledgeQuery, filters: dict[str, Any] | None = None, top_k: int = 4
    ) -> list[FashionKnowledgeHit]:
        wanted = _terms(query.concepts + query.garment_categories + query.style_tags)
        if query.text:
            wanted |= _terms([query.text])
        filters = filters or {}
        scored: list[tuple[float, dict[str, Any]]] = []
        for rec in self._records:
            occasions = rec.get("occasions") or []
            if query.occasion and occasions and query.occasion not in occasions:
                continue
            if any(rec.get(k) not in (v if isinstance(v, list) else [v]) for k, v in filters.items()):
                continue
            rec_terms = _terms(rec.get("tags", [])) | _terms([rec.get("text", "")])
            tag_terms = _terms(rec.get("tags", []))
            overlap = len(wanted & tag_terms) * 2 + len(wanted & rec_terms)
            if overlap:
                scored.append((overlap, rec))
        scored.sort(key=lambda x: (-x[0], x[1]["id"]))
        top = scored[:top_k]
        best = top[0][0] if top else 1
        return [
            FashionKnowledgeHit(
                id=r["id"],
                text=r["text"],
                score=round(s / best, 3),
                tags=r.get("tags", []),
                source_title=r.get("source_title"),
                source_url=r.get("source_url"),
                license=r.get("license"),
                provenance=r.get("provenance"),
            )
            for s, r in top
        ]


class VectorFashionKnowledgeRetriever:
    """Placeholder adapter for the future vector index (owned by the research workstream)."""

    name = "vector"

    async def search(
        self, query: FashionKnowledgeQuery, filters: dict[str, Any] | None = None, top_k: int = 4
    ) -> list[FashionKnowledgeHit]:
        raise NotImplementedError("Vector knowledge backend is not wired up yet")


async def safe_search(
    retriever: FashionKnowledgeRetriever,
    query: FashionKnowledgeQuery,
    *,
    top_k: int = 4,
    timeout_s: float = 2.0,
) -> list[FashionKnowledgeHit]:
    """Never raises: returns [] on timeout, error or bad records."""
    try:
        hits = await asyncio.wait_for(retriever.search(query, None, top_k), timeout=timeout_s)
        return [h for h in hits if isinstance(h, FashionKnowledgeHit) and h.text.strip()][:top_k]
    except Exception as exc:  # includes TimeoutError and NotImplementedError
        log.warning("knowledge retrieval skipped (%s): %s", getattr(retriever, "name", "?"), exc)
        return []


def build_query(analysis: InspirationAnalysis, prefs: StylePreferences) -> FashionKnowledgeQuery:
    concepts = ["silhouette", "proportion", "palette"]
    if analysis.layering or any(p.layer in ("mid", "outer") for p in analysis.pieces):
        concepts.append("layering")
    if prefs.fidelity == "creative":
        concepts.append("substitution")
    tags = list(analysis.aesthetic)
    for p in analysis.pieces:
        tags.extend(t for t in [p.subcategory, p.silhouette] if t)
    return FashionKnowledgeQuery(
        concepts=concepts,
        occasion=prefs.occasion,
        garment_categories=sorted({p.category for p in analysis.pieces}),
        style_tags=tags[:12],
        text=analysis.summary,
    )


@lru_cache
def get_retriever() -> FashionKnowledgeRetriever:
    s = get_settings()
    if s.fashion_knowledge_backend == "local":
        path = s.fashion_knowledge_path or DEFAULT_DATASET
        try:
            return LocalFashionKnowledgeRetriever.from_path(path)
        except Exception as exc:
            log.warning("could not load knowledge dataset %s: %s", path, exc)
            return NoOpFashionKnowledgeRetriever()
    if s.fashion_knowledge_backend == "vector":
        return VectorFashionKnowledgeRetriever()
    return NoOpFashionKnowledgeRetriever()
