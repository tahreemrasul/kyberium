from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth import get_owner
from app.demo import SAMPLE_GARMENT_IDS, SAMPLE_INSPIRATIONS, sample_garments, sample_inspiration_image_url
from app.deps import repo_dep
from app.schemas import Garment, SampleInspiration
from app.storage import Repository
from app.wardrobe import GARMENTS, list_garments

router = APIRouter(prefix="/demo", tags=["demo"])


class SeedResult(BaseModel):
    added: int
    items: list[Garment]


@router.post("/wardrobe", response_model=SeedResult)
async def load_sample_wardrobe(owner: str = Depends(get_owner), repo: Repository = Depends(repo_dep)) -> SeedResult:
    """Add any missing sample garments. Never touches the user's own uploads; edits to samples are kept."""
    existing = {d["id"] for d in await repo.list(owner, GARMENTS)}
    added = 0
    for g in sample_garments():
        if g.id not in existing:
            await repo.put(owner, GARMENTS, g.id, g.model_dump(mode="json"))
            added += 1
    return SeedResult(added=added, items=await list_garments(repo, owner))


@router.delete("/wardrobe", response_model=SeedResult)
async def remove_sample_wardrobe(owner: str = Depends(get_owner), repo: Repository = Depends(repo_dep)) -> SeedResult:
    """Remove sample garments only; uploaded garments stay."""
    removed = 0
    for gid in SAMPLE_GARMENT_IDS:
        removed += int(await repo.delete(owner, GARMENTS, gid))
    return SeedResult(added=-removed, items=await list_garments(repo, owner))


@router.get("/inspirations", response_model=list[SampleInspiration])
async def list_sample_inspirations() -> list[SampleInspiration]:
    return [
        SampleInspiration(
            id=i["id"], title=i["title"], image_url=sample_inspiration_image_url(i["id"]), scenario=i["scenario"]
        )
        for i in SAMPLE_INSPIRATIONS
    ]
