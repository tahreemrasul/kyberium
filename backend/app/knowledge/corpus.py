"""Adapter for the team's Rewear Fashion Knowledge corpus (``knowledge.jsonl``, schema v0.1.0).

Implements the lexical half of the corpus spec (retrieval_docs/Retrieval_and_Evaluation_Guide.md):

* one record = one chunk; conditions, failure cases and adjustments stay attached to the
  principle so "satin can replace denim" is never returned without its "may fail when";
* BM25 over principle, subtopic, attributes, garments, conditions, failures and adjustments;
* occasion / aesthetic act as boosts (records tagged "any" stay eligible), never hard filters;
* a compact result set (top_k) with provenance: source titles/URLs, rights status, claim type
  and review status are carried as metadata, never as instructions.

The semantic branch + Reciprocal Rank Fusion described in the spec plug in by implementing
``VectorFashionKnowledgeRetriever`` and fusing ranks; this class stays the lexical baseline.
"""

import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

from app.knowledge.retriever import FashionKnowledgeHit, FashionKnowledgeQuery

_TOKEN = re.compile(r"[a-z][a-z_-]+")
_STOP = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "when",
    "than",
    "into",
    "from",
    "are",
    "can",
    "not",
    "its",
    "use",
    "any",
    "all",
    "one",
    "more",
    "less",
    "may",
    "be",
    "or",
    "of",
    "to",
    "in",
    "on",
    "a",
    "an",
    "is",
}


def _tokens(text: str) -> list[str]:
    out = []
    for t in _TOKEN.findall(text.lower()):
        for part in t.replace("-", "_").split("_"):
            if len(part) > 2 and part not in _STOP:
                out.append(part.rstrip("s") if len(part) > 4 else part)
    return out


def _search_text(r: dict[str, Any]) -> str:
    """Deterministic search text (spec §3): title, principle, garments/attributes, context, conditions."""
    return " ".join(
        [
            r.get("topic", ""),
            r.get("subtopic", ""),
            r.get("styling_principle", ""),
            " ".join(r.get("applicable_garment_categories", [])),
            " ".join(r.get("relevant_attributes", [])),
            " ".join(r.get("styles_aesthetics", [])),
            " ".join(r.get("tags", []) or []),
            " ".join(r.get("applicable_conditions", [])),
            " ".join(r.get("counterexamples_or_failure_conditions", [])),
            " ".join(r.get("practical_styling_adjustments", [])),
        ]
    )


def render(r: dict[str, Any]) -> str:
    """Compact, self-contained text for the stylist/critic: principle + when it applies/fails + adjustment."""
    parts = [r["styling_principle"].rstrip(".") + "."]
    if r.get("applicable_conditions"):
        parts.append("Applies when: " + "; ".join(r["applicable_conditions"][:2]))
    if r.get("counterexamples_or_failure_conditions"):
        parts.append("May fail when: " + "; ".join(r["counterexamples_or_failure_conditions"][:2]))
    if r.get("practical_styling_adjustments"):
        parts.append("Adjust: " + "; ".join(r["practical_styling_adjustments"][:2]))
    return " ".join(parts)


class CorpusFashionKnowledgeRetriever:
    """BM25 retrieval over the Rewear knowledge corpus with soft occasion/aesthetic boosts."""

    name = "corpus"
    k1, b = 1.4, 0.75

    def __init__(self, records: list[dict[str, Any]]) -> None:
        self.records = [r for r in records if r.get("styling_principle")]
        self.docs = [_tokens(_search_text(r)) for r in self.records]
        self.lengths = [len(d) for d in self.docs]
        self.avg_len = sum(self.lengths) / max(1, len(self.lengths))
        self.tf = [Counter(d) for d in self.docs]
        df: Counter[str] = Counter()
        for d in self.docs:
            df.update(set(d))
        n = len(self.docs)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}

    @classmethod
    def from_path(cls, path: Path) -> "CorpusFashionKnowledgeRetriever":
        lines = Path(path).read_text("utf-8").splitlines()
        return cls([json.loads(line) for line in lines if line.strip()])

    def _bm25(self, i: int, terms: Counter[str]) -> float:
        score = 0.0
        tf, length = self.tf[i], self.lengths[i]
        for t, q in terms.items():
            f = tf.get(t)
            if not f:
                continue
            norm = f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * length / self.avg_len))
            score += self.idf.get(t, 0.0) * norm * (1 + 0.2 * (q - 1))
        return score

    async def search(
        self, query: FashionKnowledgeQuery, filters: dict[str, Any] | None = None, top_k: int = 4
    ) -> list[FashionKnowledgeHit]:
        text = " ".join([query.text or "", *query.concepts, *query.garment_categories, *query.style_tags])
        terms = Counter(_tokens(text))
        if not terms:
            return []
        styles = {s.lower() for s in query.style_tags}
        scored: list[tuple[float, int]] = []
        for i, r in enumerate(self.records):
            s = self._bm25(i, terms)
            if s <= 0:
                continue
            occasions = {o.lower() for o in r.get("occasions", [])}
            if query.occasion and query.occasion in occasions:
                s *= 1.15  # boost, not a filter (spec §4)
            if styles & {a.lower() for a in r.get("styles_aesthetics", [])}:
                s *= 1.1
            scored.append((s, i))
        scored.sort(key=lambda x: -x[0])
        seen_families: set[str] = set()
        hits: list[FashionKnowledgeHit] = []
        best = scored[0][0] if scored else 1.0
        for s, i in scored:
            r = self.records[i]
            family = f"{r.get('topic')}/{r.get('subtopic')}"
            if family in seen_families:  # deduplicate by principle family (spec §4.5)
                continue
            seen_families.add(family)
            src = (r.get("sources") or [{}])[0]
            rights = sorted({x.get("rights_status", "unknown") for x in r.get("sources", [])})
            hits.append(
                FashionKnowledgeHit(
                    id=r["id"],
                    text=render(r),
                    score=round(s / best, 3),
                    tags=[r.get("topic", ""), r.get("subtopic", ""), *r.get("relevant_attributes", [])][:8],
                    collection="Fashion Encyclopedia",
                    source_title=src.get("title"),
                    source_url=src.get("url"),
                    license=", ".join(rights),
                    provenance=f"{r.get('claim_type', 'unknown')}; {r.get('review_status', 'unreviewed')}",
                )
            )
            if len(hits) >= top_k:
                break
        return hits
