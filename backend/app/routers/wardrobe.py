import asyncio
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import Response

from app.ai.client import GeminiClient
from app.auth import get_owner
from app.config import Settings
from app.deps import ai_budget, ai_dep, blobs_dep, repo_dep, settings_dep
from app.errors import ApiError, not_found
from app.images import normalize_image
from app.pipeline.cutout import display_image
from app.pipeline.garments import analyze_garment
from app.schemas import Garment, GarmentAnalysis, GarmentCreate, GarmentUpdate
from app.storage import BlobStore, Repository
from app.wardrobe import GARMENTS, get_garment, list_garments

router = APIRouter(prefix="/wardrobe", tags=["wardrobe"])
UPLOADS = "uploads"


@router.get("/items", response_model=list[Garment])
async def list_items(owner: str = Depends(get_owner), repo: Repository = Depends(repo_dep)) -> list[Garment]:
    return await list_garments(repo, owner)


@router.post("/items/analyze", response_model=GarmentAnalysis)
async def analyze_item(
    file: UploadFile = File(...),
    owner: str = Depends(ai_budget),
    repo: Repository = Depends(repo_dep),
    blobs: BlobStore = Depends(blobs_dep),
    ai: GeminiClient | None = Depends(ai_dep),
    settings: Settings = Depends(settings_dep),
) -> GarmentAnalysis:
    """Upload one garment photo, store it, and return Gemini's draft tags for the user to confirm."""
    jpeg, sha = normalize_image(await file.read(settings.max_upload_bytes + 1), settings.max_upload_bytes)
    upload_id = "up_" + uuid.uuid4().hex[:20]
    key = f"uploads/{owner}/{upload_id}.jpg"
    await blobs.put(key, jpeg, "image/jpeg")
    # Tag the garment and build its standard-scale display image concurrently.
    analysis, (display_png, method) = await asyncio.gather(
        analyze_garment(ai, repo, owner, upload_id=upload_id, image_url=f"/media/{key}", image=jpeg, image_sha=sha),
        display_image(ai, jpeg),
    )
    display_key = f"uploads/{owner}/{upload_id}_cut.png"
    await blobs.put(display_key, display_png, "image/png")
    await repo.put(
        owner,
        UPLOADS,
        upload_id,
        {
            "id": upload_id,
            "image_key": key,
            "display_key": display_key,
            "display_method": method,
            "sha256": sha,
            "created_at": datetime.now(UTC).isoformat(),
        },
    )
    return analysis.model_copy(update={"display_url": f"/media/{display_key}"})


async def _get_upload(repo: Repository, owner: str, upload_id: str) -> dict:
    try:
        up = await repo.get(owner, UPLOADS, upload_id)
    except ValueError:
        up = None
    if not up:
        raise not_found("Upload")
    return up


@router.post("/uploads/{upload_id}/analyze", response_model=GarmentAnalysis)
async def reanalyze_upload(
    upload_id: str,
    owner: str = Depends(ai_budget),
    repo: Repository = Depends(repo_dep),
    blobs: BlobStore = Depends(blobs_dep),
    ai: GeminiClient | None = Depends(ai_dep),
) -> GarmentAnalysis:
    """Retry tagging for an already-uploaded photo (no re-upload needed)."""
    up = await _get_upload(repo, owner, upload_id)
    blob = await blobs.get(up["image_key"])
    if blob is None:
        raise not_found("Upload image")
    analysis = await analyze_garment(
        ai,
        repo,
        owner,
        upload_id=upload_id,
        image_url=f"/media/{up['image_key']}",
        image=blob[0],
        image_sha=up["sha256"],
    )
    display = f"/media/{up['display_key']}" if up.get("display_key") else None
    return analysis.model_copy(update={"display_url": display})


@router.post("/items", response_model=Garment, status_code=201)
async def create_item(
    body: GarmentCreate,
    owner: str = Depends(get_owner),
    repo: Repository = Depends(repo_dep),
    settings: Settings = Depends(settings_dep),
) -> Garment:
    """Persist a garment the user has reviewed. The image must be one of the user's own uploads."""
    up = await _get_upload(repo, owner, body.upload_id)
    if up.get("garment_id"):
        raise ApiError(409, "already_saved", "This photo is already saved in your closet.")
    if len(await repo.list(owner, GARMENTS)) >= settings.max_wardrobe_items:
        raise ApiError(409, "wardrobe_full", f"Closets are limited to {settings.max_wardrobe_items} items for now.")
    now = datetime.now(UTC)
    garment = Garment(
        **body.model_dump(exclude={"upload_id"}),
        id="g_" + uuid.uuid4().hex[:16],
        image_url=f"/media/{up.get('display_key') or up['image_key']}",
        image_kind="cutout" if up.get("display_key") else "photo",
        source="upload",
        verified_by_user=True,
        created_at=now,
        updated_at=now,
    )
    await repo.put(owner, GARMENTS, garment.id, {**garment.model_dump(mode="json"), "upload_id": body.upload_id})
    await repo.put(owner, UPLOADS, up["id"], {**up, "garment_id": garment.id})
    return garment


@router.patch("/items/{garment_id}", response_model=Garment)
async def update_item(
    garment_id: str,
    body: GarmentUpdate,
    owner: str = Depends(get_owner),
    repo: Repository = Depends(repo_dep),
) -> Garment:
    current = await get_garment(repo, owner, garment_id)
    if current is None:
        raise not_found("Garment")
    changes = {
        k: v
        for k, v in body.model_dump(exclude_unset=True).items()
        if not (v is None and k in ("name", "category", "colors", "formality"))
    }
    merged = Garment.model_validate(
        {**current.model_dump(), **changes, "updated_at": datetime.now(UTC), "verified_by_user": True}
    )
    existing = await repo.get(owner, GARMENTS, garment_id) or {}
    await repo.put(owner, GARMENTS, garment_id, {**existing, **merged.model_dump(mode="json")})
    return merged


@router.delete("/items/{garment_id}", status_code=204)
async def delete_item(
    garment_id: str,
    owner: str = Depends(get_owner),
    repo: Repository = Depends(repo_dep),
    blobs: BlobStore = Depends(blobs_dep),
) -> Response:
    try:
        doc = await repo.get(owner, GARMENTS, garment_id)
    except ValueError:
        doc = None
    if not doc:
        raise not_found("Garment")
    await repo.delete(owner, GARMENTS, garment_id)
    if doc.get("upload_id"):
        up = await repo.get(owner, UPLOADS, doc["upload_id"])
        if up:
            await blobs.delete(up["image_key"])
            if up.get("display_key"):
                await blobs.delete(up["display_key"])
            await repo.delete(owner, UPLOADS, up["id"])
    return Response(status_code=204)
