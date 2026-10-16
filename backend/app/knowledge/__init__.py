"""Optional fashion-knowledge retrieval (styling principles), separate from wardrobe retrieval."""

from app.knowledge.retriever import (
    FashionKnowledgeHit,
    FashionKnowledgeQuery,
    FashionKnowledgeRetriever,
    LocalFashionKnowledgeRetriever,
    NoOpFashionKnowledgeRetriever,
    VectorFashionKnowledgeRetriever,
    build_query,
    get_retriever,
    safe_search,
)

__all__ = [
    "FashionKnowledgeHit",
    "FashionKnowledgeQuery",
    "FashionKnowledgeRetriever",
    "LocalFashionKnowledgeRetriever",
    "NoOpFashionKnowledgeRetriever",
    "VectorFashionKnowledgeRetriever",
    "build_query",
    "get_retriever",
    "safe_search",
]
