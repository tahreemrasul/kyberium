import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from app.ai.client import GeminiClient
from app.auth import get_owner
from app.config import Settings
from app.deps import ai_budget, ai_dep, blobs_dep, repo_dep, retriever_dep, settings_dep
from app.errors import ApiError, not_found
from app.knowledge import FashionKnowledgeRetriever
from app.pipeline.orchestrator import load_generation, run_pipeline, save_generation
from app.pipeline.refine import apply_plan, plan_refinement, swap_item
from app.routers.inspirations import load_inspiration
from app.schemas import GenerateRequest, Generation, RefineRequest, SavedLook, SavedLookCreate, SwapRequest
from app.storage import BlobStore, Repository
from app.stylist.images import make_image_loader
from app.wardrobe import get_garment, wardrobe_index

router = APIRouter(prefix="/looks", tags=["looks"])
SAVED = "saved_looks"


@router.post("/generate", response_model=Generation)
async def generate(
    body: GenerateRequest,
    owner: str = Depends(ai_budget),
    repo: Repository = Depends(repo_dep),
    ai: GeminiClient | None = Depends(ai_dep),
    retriever: FashionKnowledgeRetriever = Depends(retriever_dep),
    settings: Settings = Depends(settings_dep),
    blobs: BlobStore = Depends(blobs_dep),
) -> Generation:
    """Recreate an analysed inspiration from the user's own wardrobe."""
    insp = await load_inspiration(repo, owner, body.inspiration_id)
    gen = await run_pipeline(
        ai=ai,
        settings=settings,
        retriever=retriever,
        image_loader=make_image_loader(blobs),
        wardrobe=await wardrobe_index(repo, owner),
        analysis=insp.analysis,
        prefs=body.preferences,
        inspiration_id=insp.id,
        inspiration_image_url=insp.image_url,
    )
    await save_generation(repo, owner, gen)
    return gen


@router.get("/generations/{generation_id}", response_model=Generation)
async def get_generation(
    generation_id: str, owner: str = Depends(get_owner), repo: Repository = Depends(repo_dep)
) -> Generation:
    return await load_generation(repo, owner, generation_id)


@router.post("/refine", response_model=Generation)
async def refine(
    body: RefineRequest,
    owner: str = Depends(ai_budget),
    repo: Repository = Depends(repo_dep),
    ai: GeminiClient | None = Depends(ai_dep),
    retriever: FashionKnowledgeRetriever = Depends(retriever_dep),
    settings: Settings = Depends(settings_dep),
    blobs: BlobStore = Depends(blobs_dep),
) -> Generation:
    """Turn a short request ("keep the blazer, change the trousers") into constraints and restyle."""
    gen = await load_generation(repo, owner, body.generation_id)
    wardrobe = await wardrobe_index(repo, owner)
    look = next((lk for lk in gen.looks if lk.id == body.look_id), gen.looks[0] if gen.looks else None)
    plan = await plan_refinement(ai, body.instruction, gen, look, wardrobe)
    prefs = apply_plan(gen.preferences, plan, wardrobe)
    new = await run_pipeline(
        ai=ai,
        settings=settings,
        retriever=retriever,
        image_loader=make_image_loader(blobs),
        wardrobe=wardrobe,
        analysis=gen.analysis,
        prefs=prefs,
        inspiration_id=gen.inspiration_id,
        inspiration_image_url=gen.inspiration_image_url,
        extra_note=plan.summary,
    )
    await save_generation(repo, owner, new)
    return new


@router.post("/swap", response_model=Generation)
async def swap(body: SwapRequest, owner: str = Depends(get_owner), repo: Repository = Depends(repo_dep)) -> Generation:
    """Replace one garment in a look with another owned garment and refresh its explanation and counts."""
    gen = await load_generation(repo, owner, body.generation_id)
    new_garment = await get_garment(repo, owner, body.new_garment_id)
    if new_garment is None:
        raise ApiError(400, "invalid_swap", "You can only swap in garments from your own closet.")
    swap_item(gen, body.look_id, body.old_garment_id, new_garment)
    await save_generation(repo, owner, gen)
    return gen


@router.get("/saved", response_model=list[SavedLook])
async def list_saved(owner: str = Depends(get_owner), repo: Repository = Depends(repo_dep)) -> list[SavedLook]:
    looks = [SavedLook.model_validate(d) for d in await repo.list(owner, SAVED)]
    return sorted(looks, key=lambda s: s.created_at, reverse=True)


@router.post("/saved", response_model=SavedLook, status_code=201)
async def save_look(
    body: SavedLookCreate, owner: str = Depends(get_owner), repo: Repository = Depends(repo_dep)
) -> SavedLook:
    gen = await load_generation(repo, owner, body.generation_id)
    look = next((lk for lk in gen.looks if lk.id == body.look_id), None)
    if look is None:
        raise not_found("Look")
    saved = SavedLook(
        id="sl_" + uuid.uuid4().hex[:16],
        generation_id=gen.id,
        inspiration_image_url=gen.inspiration_image_url,
        preferences=gen.preferences,
        look=look,
        created_at=datetime.now(UTC),
    )
    await repo.put(owner, SAVED, saved.id, saved.model_dump(mode="json"))
    return saved


@router.delete("/saved/{saved_id}", status_code=204)
async def delete_saved(
    saved_id: str, owner: str = Depends(get_owner), repo: Repository = Depends(repo_dep)
) -> Response:
    try:
        ok = await repo.delete(owner, SAVED, saved_id)
    except ValueError:
        ok = False
    if not ok:
        raise not_found("Saved look")
    return Response(status_code=204)
