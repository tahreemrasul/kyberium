# Plugging in the fashion-knowledge index

This guide is for the research/data workstream that is building the styling-knowledge vector index. The app already calls a retriever at the right point in the pipeline. You implement one class and change one environment variable. No endpoint or UI changes are needed.

## Where it runs

```
Inspiration analysis → build_query() → retriever.search() → wardrobe matching + Gemini composition
```

- Code: `backend/app/knowledge/retriever.py`
- Selection: `FASHION_KNOWLEDGE_BACKEND=none|local|vector`
- Call site: `app/pipeline/orchestrator.py` → `safe_search(retriever, query, top_k, timeout_s)`

## Contract

```python
class FashionKnowledgeQuery(BaseModel):
    concepts: list[str]            # e.g. silhouette, proportion, palette, layering, substitution
    occasion: str | None           # work | everyday | event | travel
    garment_categories: list[str]  # categories present in the inspiration
    style_tags: list[str]          # aesthetic + piece subtypes/silhouettes
    text: str | None               # inspiration summary, for semantic search

class FashionKnowledgeHit(BaseModel):
    id: str
    text: str                      # a concise styling principle
    score: float | None            # ranking value, NOT a probability
    tags: list[str]
    source_title: str | None
    source_url: str | None
    license: str | None
    provenance: str | None

class FashionKnowledgeRetriever(Protocol):
    name: str
    async def search(self, query, filters=None, top_k=4) -> list[FashionKnowledgeHit]: ...
```

## Implementing the vector adapter

1. Fill in `VectorFashionKnowledgeRetriever.search` using pgvector, Qdrant or Vertex AI Vector Search. Embed `query.text` together with the concepts and tags, filter on `occasion` when the record has occasions, and return at most `top_k` hits.
2. Read connection settings from new environment variables inside the adapter. Business logic must not import the vector client.
3. Set `FASHION_KNOWLEDGE_BACKEND=vector`.
4. Add a test next to `backend/tests/test_knowledge.py` that runs your adapter with a test double. The existing tests already prove that the pipeline works with no hits, with errors and with timeouts.

## Guarantees the app enforces (please keep them)

- **Best-effort:** `safe_search` applies a 2-second timeout (configurable) and returns `[]` on any error, so a slow or broken index never blocks styling.
- **Separate from the wardrobe:** hits are passed to the composer as `styling_principles`. The validation layer drops any garment ID that isn't in the user's closet, so knowledge can never create an "owned" item.
- **Provenance:** hits are shown to the user under "Styling principles considered", with `source_title` and `source_url`. Only index material you have the right to use, store its licence, and never fabricate citations. As the PRD notes, Condé Nast (Vogue) terms prohibit automated harvesting.
- **Measured value:** compare `uv run python -m evals.run_evals --live` with `FASHION_KNOWLEDGE_BACKEND=none` and with `=vector` before you switch the default.

The bundled `local` dataset (`app/knowledge/data/styling_principles.json`) holds 20 original cards written by the team, in the same record shape your index should return.
