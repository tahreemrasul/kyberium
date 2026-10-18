"""Shared API contracts. Mirrored in frontend/src/lib/types.ts — keep in sync.

Two families of models live here:
  * Model-output schemas (``*Draft``/``Composed*``/``InspirationAnalysis``) that
    Gemini must fill. They are always re-validated server-side.
  * API resources (``Garment``, ``Look`` …) that the server builds itself.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Category = Literal["top", "bottom", "outerwear", "dress", "shoes", "accessory"]
Formality = Literal["casual", "smart_casual", "formal"]
Layer = Literal["base", "mid", "outer", "none"]
Occasion = Literal["work", "everyday", "event", "travel"]
Fidelity = Literal["close", "aesthetic", "creative"]
Shopping = Literal["wardrobe_first", "secondhand_rental", "open_to_new"]
Strategy = Literal["closest", "creative", "alternative"]
# "agentic" = ADK stylist–critic workflow; "gemini" = single-pass composer; "rules" = labelled fallback
Engine = Literal["agentic", "gemini", "rules"]

CATEGORIES: tuple[str, ...] = ("top", "bottom", "outerwear", "dress", "shoes", "accessory")


def _clean_list(values: list[str], limit: int) -> list[str]:
    seen: list[str] = []
    for v in values:
        v = " ".join(str(v).split()).strip().lower()[:40]
        if v and v not in seen:
            seen.append(v)
    return seen[:limit]


def _clean_text(v: str | None) -> str | None:
    if v is None:
        return None
    v = " ".join(v.split()).strip()
    return v or None


class ApiModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


# ---------------------------------------------------------------------------
# Garments
# ---------------------------------------------------------------------------


class GarmentAttributes(ApiModel):
    """Visual attributes of one garment. Shared by AI drafts and saved items."""

    name: str = Field(min_length=1, max_length=80, description="Short descriptive name, e.g. 'Sage tailored blazer'")
    category: Category
    subcategory: str | None = Field(default=None, max_length=40, description="e.g. blazer, jeans, loafers")
    colors: list[str] = Field(min_length=1, description="Colour names, primary colour first")
    silhouette: str | None = Field(default=None, max_length=60, description="Cut/fit, e.g. relaxed, slim, wide-leg")
    pattern: str | None = Field(default=None, max_length=40)
    formality: Formality
    layer: Layer = "none"
    style_tags: list[str] = Field(default_factory=list)
    occasions: list[Occasion] = Field(default_factory=list)
    material_appearance: str | None = Field(
        default=None, max_length=60, description="What the fabric looks like. Never a verified composition."
    )

    @field_validator("colors")
    @classmethod
    def _colors(cls, v: list[str]) -> list[str]:
        cleaned = _clean_list(v, 4)
        if not cleaned:
            raise ValueError("at least one colour is required")
        return cleaned

    @field_validator("style_tags")
    @classmethod
    def _tags(cls, v: list[str]) -> list[str]:
        return _clean_list(v, 8)

    @field_validator("occasions")
    @classmethod
    def _occasions(cls, v: list[str]) -> list[str]:
        return list(dict.fromkeys(v))

    @field_validator("subcategory", "silhouette", "pattern", "material_appearance", mode="before")
    @classmethod
    def _strip_optional(cls, v: str | None) -> str | None:
        return _clean_text(v)[:60] if isinstance(v, str) and _clean_text(v) else None

    @field_validator("name", mode="before")
    @classmethod
    def _strip_name(cls, v: str) -> str:
        return (_clean_text(v) or "")[:80] if isinstance(v, str) else v


class GarmentDraft(GarmentAttributes):
    """Gemini's proposed tags for an uploaded photo; the user confirms/edits."""

    is_garment: bool = Field(default=True, description="False if the photo does not show a single clothing item")
    low_confidence_fields: list[str] = Field(default_factory=list)
    notes: str | None = Field(default=None, max_length=300)


class GarmentAnalysis(ApiModel):
    """Response of POST /wardrobe/items/analyze."""

    upload_id: str
    image_url: str
    display_url: str | None = Field(
        default=None, description="Garment cut out / cropped and placed at a standard scale on the studio background"
    )
    draft: GarmentDraft | None
    engine: Literal["gemini", "none"]
    cached: bool = False
    message: str | None = None


class GarmentCreate(GarmentAttributes):
    upload_id: str


class GarmentUpdate(ApiModel):
    name: str | None = None
    category: Category | None = None
    subcategory: str | None = None
    colors: list[str] | None = None
    silhouette: str | None = None
    pattern: str | None = None
    formality: Formality | None = None
    layer: Layer | None = None
    style_tags: list[str] | None = None
    occasions: list[Occasion] | None = None
    material_appearance: str | None = None


class Garment(GarmentAttributes):
    id: str
    image_url: str
    image_kind: Literal["photo", "cutout", "illustration"] = "photo"
    source: Literal["upload", "sample"] = "upload"
    verified_by_user: bool = True
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Inspiration
# ---------------------------------------------------------------------------


class InspirationPiece(ApiModel):
    slot_id: str = Field(description="Stable id like 'outerwear-1'")
    category: Category
    description: str = Field(max_length=160)
    subcategory: str | None = None
    colors: list[str] = Field(default_factory=list)
    silhouette: str | None = None
    pattern: str | None = None
    formality: Formality
    layer: Layer = "none"
    style_tags: list[str] = Field(default_factory=list)
    visibility: Literal["clear", "partial", "obscured"] = "clear"
    importance: Literal["key", "supporting"] = "key"
    material_appearance: str | None = Field(default=None, description="e.g. rigid mid-wash denim, fluid satin")
    fit_volume: str | None = Field(default=None, description="e.g. cropped and boxy, fitted, voluminous")
    styling_details: list[str] = Field(
        default_factory=list, description="How it is worn, e.g. 'tucked in', 'sleeves rolled', 'worn open'"
    )

    @field_validator("colors", "style_tags")
    @classmethod
    def _lists(cls, v: list[str]) -> list[str]:
        return _clean_list(v, 8)


class InspirationAnalysis(ApiModel):
    is_outfit: bool = Field(description="False if no wearable outfit is visible")
    summary: str = Field(max_length=500)
    aesthetic: list[str] = Field(default_factory=list)
    palette: list[str] = Field(default_factory=list)
    proportions: str | None = Field(default=None, max_length=400)
    layering: str | None = Field(default=None, max_length=400)
    formality: Formality
    occasions: list[Occasion] = Field(default_factory=list)
    pieces: list[InspirationPiece] = Field(default_factory=list, max_length=8)
    ambiguities: list[str] = Field(default_factory=list, max_length=6)
    # --- Outfit DNA: what makes the look work, beyond individual garments ---------
    essential_traits: list[str] = Field(
        default_factory=list,
        description="Characteristics the look loses its identity without, e.g. 'defined waist', "
        "'elongated lower half', 'relaxed but put-together'",
    )
    flexible_traits: list[str] = Field(
        default_factory=list,
        description="What can change without losing the aesthetic, e.g. 'exact skirt colour', 'sneaker brand'",
    )
    waist_definition: str | None = Field(default=None, description="Where/how the waist is marked, or 'undefined'")
    volume_balance: str | None = Field(default=None, description="How volume is distributed top vs bottom")
    color_contrast: str | None = Field(default=None, description="e.g. 'high: crisp white against mid blue'")
    materials: list[str] = Field(default_factory=list, description="Visible fabric appearances and their interplay")
    styling_details: list[str] = Field(
        default_factory=list, description="Outfit-level styling moves, e.g. 'shirt fully tucked', 'sleeves pushed up'"
    )

    @field_validator("aesthetic", "palette")
    @classmethod
    def _lists(cls, v: list[str]) -> list[str]:
        return _clean_list(v, 6)

    @field_validator("occasions")
    @classmethod
    def _occasions(cls, v: list[str]) -> list[str]:
        return list(dict.fromkeys(v))


class Inspiration(ApiModel):
    """Response of POST /inspirations."""

    id: str
    image_url: str
    analysis: InspirationAnalysis
    engine: Literal["gemini", "cached_sample"]
    sample_id: str | None = None
    created_at: datetime


class SampleInspiration(ApiModel):
    id: str
    title: str
    image_url: str
    scenario: str


# ---------------------------------------------------------------------------
# Preferences & looks
# ---------------------------------------------------------------------------


class StylePreferences(ApiModel):
    occasion: Occasion = "work"
    fidelity: Fidelity = "aesthetic"
    shopping: Shopping = "wardrobe_first"
    keep_garment_ids: list[str] = Field(default_factory=list, max_length=10)
    exclude_garment_ids: list[str] = Field(default_factory=list, max_length=40)
    notes: str | None = Field(default=None, max_length=300, description="Free-text refinement, e.g. 'more colourful'")


class CandidateMatch(ApiModel):
    garment_id: str
    slot_id: str
    score: float = Field(description="Relative ranking value in [0,1]. NOT a probability.")
    reasons: list[str]
    matching_attributes: list[str] = Field(default_factory=list)
    differences: list[str] = Field(default_factory=list)
    styling_considerations: list[str] = Field(default_factory=list)


class RoleCandidate(ApiModel):
    """One owned garment that can fill SEVERAL inspiration roles at once (e.g. a dress for top + skirt)."""

    garment_id: str
    covers_slot_ids: list[str]
    score: float = Field(description="Relative ranking value in [0,1]. NOT a probability.")
    matching_attributes: list[str] = Field(default_factory=list)
    differences: list[str] = Field(default_factory=list)
    styling_considerations: list[str] = Field(default_factory=list)


class ComposedItem(ApiModel):
    garment_id: str
    replaces_slot_id: str | None = Field(
        default=None, description="Inspiration slot this garment stands in for; null if an added piece"
    )
    covers_slot_ids: list[str] = Field(
        default_factory=list,
        description="Other inspiration slots this ONE garment also fulfils (e.g. a shirt-dress: top-1 and bottom-1)",
    )
    role: str | None = Field(default=None, description="The garment's job in this outfit, e.g. 'crisp base layer'")
    explanation: str
    preserved: list[str] = Field(default_factory=list)
    changed: list[str] = Field(default_factory=list)


class ComposedGap(ApiModel):
    slot_id: str
    reason: str
    essential: bool = Field(description="True if the look clearly suffers without it")


class ComposedLook(ApiModel):
    strategy: Strategy
    title: str
    items: list[ComposedItem]
    gaps: list[ComposedGap] = Field(default_factory=list)
    why_it_works: list[str] = Field(default_factory=list)
    styling_tip: str | None = None
    coherence: str | None = Field(
        default=None, description="How the pieces work TOGETHER: silhouette, proportion, palette, texture, formality"
    )
    styling_instructions: list[str] = Field(
        default_factory=list, description="Actionable wearing instructions, e.g. 'front-tuck the sweater'"
    )
    preserved_traits: list[str] = Field(default_factory=list, description="Inspiration essential traits kept")
    deviations: list[str] = Field(default_factory=list, description="Significant intentional differences")


class CompositionResult(ApiModel):
    looks: list[ComposedLook]
    no_match_reason: str | None = None


# ---------------------------------------------------------------------------
# Fashion critic
# ---------------------------------------------------------------------------

Criterion = Literal[
    "coherence",
    "proportion",
    "compatibility",
    "color_texture",
    "fidelity",
    "preferences",
    "occasion",
    "creativity",
    "sustainability",
]


class CriticIssue(ApiModel):
    criterion: Criterion
    severity: Literal["minor", "major", "critical"]
    problem: str
    suggested_fix: str | None = None
    fixable_with_wardrobe: bool = Field(
        default=True,
        description="False if no owned garment or styling change could fix it (e.g. the colour simply isn't owned)",
    )


class LookEvaluation(ApiModel):
    look_index: int = Field(description="Index of the look in the list under review (0-based)")
    verdict: Literal["approve", "revise", "reject"]
    strengths: list[str] = Field(default_factory=list)
    issues: list[CriticIssue] = Field(default_factory=list)


class CriticReport(ApiModel):
    evaluations: list[LookEvaluation]
    summary: str


class LookReview(ApiModel):
    """The critic's verdict as shown to users (ratings are not objective quality scores)."""

    verdict: Literal["approve", "revise", "reject"]
    strengths: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list, description="Minor issues the critic accepted")
    rounds: int = Field(default=0, description="Refinement rounds this look went through")


class TraceStep(ApiModel):
    step: str
    round: int
    summary: str
    details: list[str] = Field(default_factory=list)
    latency_ms: int | None = None
    tokens: int | None = None


class StylingTrace(ApiModel):
    engine: str
    rounds: int
    steps: list[TraceStep] = Field(default_factory=list)
    total_latency_ms: int | None = None
    total_tokens: int | None = None
    final_decision: str | None = None


class LookItem(ApiModel):
    garment_id: str
    garment: Garment
    replaces_slot_id: str | None
    replaces_description: str | None
    explanation: str
    preserved: list[str]
    changed: list[str]
    role: str | None = None
    covers_slot_ids: list[str] = Field(default_factory=list)


class LookGap(ApiModel):
    slot_id: str
    description: str
    category: Category
    reason: str
    essential: bool
    # Present only when the shopping preference allows looking outside the
    # closet. Always a *search idea*, never a specific product claim.
    sourcing_hint: str | None = None


class ImpactSummary(ApiModel):
    owned_count: int
    total_pieces: int
    gap_count: int
    essential_gap_count: int
    purchase_needed: bool
    potential_purchases_avoided: int = Field(description="Inspiration pieces covered by owned garments; an estimate")
    headline: str


class Look(ApiModel):
    id: str
    strategy: Strategy
    title: str
    items: list[LookItem]
    gaps: list[LookGap]
    why_it_works: list[str]
    styling_tip: str | None
    impact: ImpactSummary
    warnings: list[str] = Field(default_factory=list)
    coherence: str | None = None
    styling_instructions: list[str] = Field(default_factory=list)
    preserved_traits: list[str] = Field(default_factory=list)
    deviations: list[str] = Field(default_factory=list)
    review: LookReview | None = None


class KnowledgeHitRef(ApiModel):
    id: str
    text: str
    source_title: str | None = None
    source_url: str | None = None


class Generation(ApiModel):
    """Response of POST /looks/generate, /looks/refine and /looks/swap."""

    id: str
    inspiration_id: str
    inspiration_image_url: str
    analysis: InspirationAnalysis
    preferences: StylePreferences
    looks: list[Look]
    candidates: dict[str, list[CandidateMatch]]
    engine: Engine
    engine_note: str | None = None
    no_match_reason: str | None = None
    knowledge: list[KnowledgeHitRef] = Field(default_factory=list)
    trace: StylingTrace | None = None
    timings: dict[str, int] = Field(
        default_factory=dict, description="Per-stage latency (ms) and token/image counts, for cost analysis"
    )
    created_at: datetime


class GenerateRequest(ApiModel):
    inspiration_id: str
    preferences: StylePreferences = Field(default_factory=StylePreferences)


class RefineRequest(ApiModel):
    generation_id: str
    instruction: str = Field(min_length=2, max_length=300)
    look_id: str | None = None


class RefinementPlan(ApiModel):
    """Gemini's structured translation of a free-text refinement request."""

    occasion: Occasion | None = None
    fidelity: Fidelity | None = None
    shopping: Shopping | None = None
    keep_garment_ids: list[str] = Field(default_factory=list)
    exclude_garment_ids: list[str] = Field(default_factory=list)
    notes: str | None = None
    summary: str


class SwapRequest(ApiModel):
    generation_id: str
    look_id: str
    old_garment_id: str
    new_garment_id: str


class SavedLookCreate(ApiModel):
    generation_id: str
    look_id: str


class SavedLook(ApiModel):
    id: str
    generation_id: str
    inspiration_image_url: str
    preferences: StylePreferences
    look: Look
    created_at: datetime


class Session(ApiModel):
    token: str


class Health(ApiModel):
    status: Literal["ok"]
    version: str
    ai_enabled: bool
    ai_model: str | None
    storage_backend: str
    knowledge_backend: str


class ErrorBody(ApiModel):
    code: str
    message: str
    retryable: bool = False
    details: dict | None = None


class ErrorEnvelope(ApiModel):
    error: ErrorBody
