import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.ai.client import GeminiClient
from app.auth import get_owner
from app.config import Settings
from app.demo import SAMPLE_INSPIRATION_INDEX, sample_inspiration_image_url
from app.deps import ai_budget, ai_dep, blobs_dep, repo_dep, settings_dep
from app.errors import ApiError, not_found
from app.images import normalize_image
from app.pipeline.inspiration import analyze_inspiration
from app.schemas import Inspiration
from app.storage import BlobStore, Repository

router = APIRouter(prefix="/inspirations", tags=["inspirations"])
INSPIRATIONS = "inspirations"


@router.post("", response_model=Inspiration, status_code=201)
async def create_inspiration(
    file: UploadFile | None = File(default=None),
    sample_id: str | None = Form(default=None),
    owner: str = Depends(ai_budget),
    repo: Repository = Depends(repo_dep),
    blobs: BlobStore = Depends(blobs_dep),
    ai: GeminiClient | None = Depends(ai_dep),
    settings: Settings = Depends(settings_dep),
) -> Inspiration:
    """Upload an inspiration photo (or pick a sample) and deconstruct it into outfit slots."""
    now = datetime.now(UTC)
    insp_id = "in_" + uuid.uuid4().hex[:20]
    if sample_id:
        sample = SAMPLE_INSPIRATION_INDEX.get(sample_id)
        if sample is None:
            raise not_found("Sample inspiration")
        insp = Inspiration(
            id=insp_id,
            image_url=sample_inspiration_image_url(sample_id),
            analysis=sample["analysis"],
            engine="cached_sample",
            sample_id=sample_id,
            created_at=now,
        )
    elif file is not None:
        jpeg, sha = normalize_image(await file.read(settings.max_upload_bytes + 1), settings.max_upload_bytes)
        key = f"inspirations/{owner}/{insp_id}.jpg"
        analysis = await analyze_inspiration(ai, repo, owner, image=jpeg, image_sha=sha)
        await blobs.put(key, jpeg, "image/jpeg")
        insp = Inspiration(id=insp_id, image_url=f"/media/{key}", analysis=analysis, engine="gemini", created_at=now)
    else:
        raise ApiError(400, "missing_image", "Upload an inspiration image or choose a sample.")
    await repo.put(owner, INSPIRATIONS, insp.id, insp.model_dump(mode="json"))
    return insp


async def load_inspiration(repo: Repository, owner: str, inspiration_id: str) -> Inspiration:
    try:
        doc = await repo.get(owner, INSPIRATIONS, inspiration_id)
    except ValueError:
        doc = None
    if not doc:
        raise not_found("Inspiration")
    return Inspiration.model_validate(doc)


@router.get("/{inspiration_id}", response_model=Inspiration)
async def get_inspiration(
    inspiration_id: str, owner: str = Depends(get_owner), repo: Repository = Depends(repo_dep)
) -> Inspiration:
    return await load_inspiration(repo, owner, inspiration_id)
