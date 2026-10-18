"""Owner-scoped wardrobe access helpers shared by routers and the pipeline."""

import logging

from pydantic import ValidationError

from app.schemas import Garment
from app.storage import Repository

log = logging.getLogger("rewear")

GARMENTS = "garments"


async def list_garments(repo: Repository, owner: str) -> list[Garment]:
    out: list[Garment] = []
    for doc in await repo.list(owner, GARMENTS):
        try:
            out.append(Garment.model_validate(doc))
        except ValidationError as exc:  # never let one bad record break the closet
            log.warning("skipping invalid garment doc %s: %s", doc.get("id"), exc)
    out.sort(key=lambda g: g.created_at, reverse=True)
    return out


async def wardrobe_index(repo: Repository, owner: str) -> dict[str, Garment]:
    return {g.id: g for g in await list_garments(repo, owner)}


async def get_garment(repo: Repository, owner: str, garment_id: str) -> Garment | None:
    try:
        doc = await repo.get(owner, GARMENTS, garment_id)
    except ValueError:
        return None
    return Garment.model_validate(doc) if doc else None
