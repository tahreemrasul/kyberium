import asyncio

import pytest

from app.config import Settings
from app.demo import SAMPLE_INSPIRATION_INDEX
from app.knowledge import (
    FashionKnowledgeHit,
    FashionKnowledgeQuery,
    LocalFashionKnowledgeRetriever,
    NoOpFashionKnowledgeRetriever,
    VectorFashionKnowledgeRetriever,
    build_query,
    safe_search,
)
from app.knowledge.retriever import DEFAULT_DATASET
from app.pipeline.orchestrator import run_pipeline
from app.schemas import StylePreferences

CAMEL = SAMPLE_INSPIRATION_INDEX["insp_camel_work"]["analysis"]


async def test_noop_returns_nothing():
    assert await NoOpFashionKnowledgeRetriever().search(FashionKnowledgeQuery(concepts=["silhouette"])) == []


async def test_local_dataset_returns_attributed_hits():
    r = LocalFashionKnowledgeRetriever.from_path(DEFAULT_DATASET)
    hits = await r.search(build_query(CAMEL, StylePreferences(occasion="work")), top_k=3)
    assert 0 < len(hits) <= 3
    for h in hits:
        assert h.text and h.provenance and h.license
        assert h.score is not None and 0 < h.score <= 1


async def test_local_respects_occasion_filter():
    r = LocalFashionKnowledgeRetriever(
        [
            {"id": "a", "text": "event only", "tags": ["blazer"], "occasions": ["event"]},
            {"id": "b", "text": "any", "tags": ["blazer"], "occasions": []},
        ]
    )
    hits = await r.search(FashionKnowledgeQuery(style_tags=["blazer"], occasion="work"))
    assert [h.id for h in hits] == ["b"]


async def test_corpus_retriever_keeps_conditions_and_provenance():
    from app.knowledge.corpus import CorpusFashionKnowledgeRetriever

    records = [
        {
            "id": "K1",
            "topic": "textile",
            "subtopic": "denim_to_satin",
            "styling_principle": "Satin can replace denim when length matters more than structure.",
            "applicable_conditions": ["The skirt is not defined by rigid seams."],
            "counterexamples_or_failure_conditions": ["Adds gloss that reads too dressy."],
            "practical_styling_adjustments": ["Pair with a matte knit and flat shoes."],
            "relevant_attributes": ["drape", "sheen"],
            "applicable_garment_categories": ["skirt"],
            "styles_aesthetics": ["any"],
            "occasions": ["any"],
            "claim_type": "styling_synthesis",
            "review_status": "desk_reviewed_not_expert_validated",
            "sources": [{"title": "Source A", "url": "https://example.org/a", "rights_status": "not_established"}],
        },
        {
            "id": "K2",
            "topic": "color",
            "subtopic": "neutrals",
            "styling_principle": "Neutral is a role, not a colour.",
            "occasions": ["work"],
            "sources": [],
        },
    ]
    r = CorpusFashionKnowledgeRetriever(records)
    hits = await r.search(FashionKnowledgeQuery(text="replace a denim skirt with a satin skirt", concepts=["texture"]))
    assert hits[0].id == "K1"
    assert "May fail when" in hits[0].text and "Adjust" in hits[0].text  # conditions travel with the principle
    assert hits[0].source_url == "https://example.org/a" and "not_established" in hits[0].license
    assert await r.search(FashionKnowledgeQuery()) == []


class Slow:
    name = "slow"

    async def search(self, query, filters=None, top_k=4):
        await asyncio.sleep(5)
        return []


class Broken:
    name = "broken"

    async def search(self, query, filters=None, top_k=4):
        raise RuntimeError("index down")


@pytest.mark.parametrize("retriever", [Slow(), Broken(), VectorFashionKnowledgeRetriever()])
async def test_safe_search_never_raises(retriever):
    assert await safe_search(retriever, FashionKnowledgeQuery(), timeout_s=0.05) == []


class Fixed:
    name = "fixed"

    def __init__(self, hits):
        self.hits = hits

    async def search(self, query, filters=None, top_k=4):
        return self.hits


async def test_pipeline_runs_with_and_without_knowledge(wardrobe):
    settings = Settings(ai_backend="off", fashion_knowledge_backend="none")
    common = dict(
        ai=None,
        settings=settings,
        wardrobe=wardrobe,
        analysis=CAMEL,
        prefs=StylePreferences(),
        inspiration_id="in_x",
        inspiration_image_url="/x",
    )
    empty = await run_pipeline(retriever=NoOpFashionKnowledgeRetriever(), **common)
    assert empty.looks and empty.knowledge == []

    hit = FashionKnowledgeHit(id="k1", text="Balance volume.", source_title="T", source_url="https://example.org")
    with_hits = await run_pipeline(retriever=Fixed([hit]), **common)
    assert [k.id for k in with_hits.knowledge] == ["k1"]
    # Knowledge never becomes wardrobe inventory.
    owned = {i.garment_id for lk in with_hits.looks for i in lk.items}
    assert owned <= set(wardrobe)

    broken = await run_pipeline(retriever=Broken(), **common)
    assert broken.looks
