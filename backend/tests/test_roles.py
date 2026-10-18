"""Role-level substitution: one garment filling several inspiration roles."""

from datetime import UTC, datetime

from app.pipeline.roles import rank_role_candidates
from app.pipeline.validation import build_look
from app.schemas import ComposedItem, ComposedLook, Garment, InspirationAnalysis, StylePreferences

NOW = datetime.now(UTC)


def garment(gid, category, name, **kw) -> Garment:
    base = dict(colors=["navy"], formality="smart_casual", style_tags=[], occasions=["everyday"])
    return Garment(
        id=gid, category=category, name=name, image_url="/x", created_at=NOW, updated_at=NOW, **{**base, **kw}
    )


TUCKED_SEPARATES = InspirationAnalysis.model_validate(
    {
        "is_outfit": True,
        "summary": "Striped blouse tucked into a pleated midi skirt.",
        "formality": "smart_casual",
        "occasions": ["everyday"],
        "aesthetic": ["polished"],
        "waist_definition": "marked by the tuck at the natural waist",
        "pieces": [
            {
                "slot_id": "top-1",
                "category": "top",
                "description": "Striped blouse",
                "subcategory": "blouse",
                "colors": ["navy", "white"],
                "formality": "smart_casual",
                "styling_details": ["tucked in"],
            },
            {
                "slot_id": "bottom-1",
                "category": "bottom",
                "description": "Pleated midi skirt",
                "subcategory": "skirt",
                "colors": ["navy"],
                "silhouette": "a-line midi",
                "formality": "smart_casual",
            },
            {
                "slot_id": "shoes-1",
                "category": "shoes",
                "description": "Loafers",
                "colors": ["black"],
                "formality": "smart_casual",
            },
        ],
    }
)

WARDROBE = [
    garment("belted", "dress", "Navy belted midi dress", silhouette="a-line midi, belted waist"),
    garment("shift", "dress", "Navy shift dress", silhouette="straight, above knee"),
    garment("gown", "dress", "Sequin gown", formality="formal", occasions=["event"], silhouette="column, maxi"),
    garment("tee", "top", "Grey tee", formality="casual"),
]


def test_one_piece_is_scored_against_the_pair():
    ranked = rank_role_candidates(TUCKED_SEPARATES, WARDROBE, StylePreferences(occasion="everyday"))
    assert ranked[0].garment_id == "belted"  # marks the waist and keeps the midi line
    assert ranked[0].covers_slot_ids == ["top-1", "bottom-1"]
    assert any("waist" in m for m in ranked[0].matching_attributes)
    shift = next((r for r in ranked if r.garment_id == "shift"), None)
    assert shift is None or shift.score < ranked[0].score
    assert all(r.garment_id != "tee" for r in ranked)  # only one-piece garments take on two roles


def test_no_role_candidates_when_inspiration_is_already_a_dress():
    dress_piece = TUCKED_SEPARATES.pieces[0].model_copy(update={"category": "dress", "slot_id": "dress-1"})
    dressy = TUCKED_SEPARATES.model_copy(update={"pieces": [dress_piece]})
    assert rank_role_candidates(dressy, WARDROBE, StylePreferences()) == []


def test_validation_credits_every_covered_slot():
    wardrobe = {g.id: g for g in WARDROBE + [garment("loafers", "shoes", "Black loafers", colors=["black"])]}
    composed = ComposedLook(
        strategy="creative",
        title="One-piece",
        items=[
            ComposedItem(garment_id="belted", replaces_slot_id="top-1", covers_slot_ids=["bottom-1"], explanation="x"),
            ComposedItem(garment_id="loafers", replaces_slot_id="shoes-1", explanation="x"),
        ],
    )
    look = build_look(composed, wardrobe, TUCKED_SEPARATES, StylePreferences())
    assert look.gaps == [] and not look.impact.purchase_needed
    assert look.items[0].replaces_description == "Striped blouse + Pleated midi skirt"
    assert look.impact.potential_purchases_avoided == 3


def test_a_top_cannot_claim_the_bottom_role():
    wardrobe = {g.id: g for g in WARDROBE}
    composed = ComposedLook(
        strategy="creative",
        title="Bad",
        items=[ComposedItem(garment_id="tee", replaces_slot_id="top-1", covers_slot_ids=["bottom-1"], explanation="x")],
    )
    look = build_look(composed, wardrobe, TUCKED_SEPARATES, StylePreferences(occasion="everyday"))
    assert look.items[0].covers_slot_ids == []
    assert "bottom-1" in {g.slot_id for g in look.gaps}
