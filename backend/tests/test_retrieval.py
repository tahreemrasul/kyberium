from app.demo import SAMPLE_INSPIRATION_INDEX
from app.pipeline.attributes import color_family, color_similarity, occasion_fit, silhouette_similarity, subtype
from app.pipeline.retrieval import rank_candidates
from app.schemas import StylePreferences


def analysis(sample_id: str):
    return SAMPLE_INSPIRATION_INDEX[sample_id]["analysis"]


def test_color_families():
    assert color_family("Sage green") == "green"
    assert color_family("camel") == "beige"
    assert color_family("light-wash blue") == "blue"
    assert color_family("champagne") == "cream"
    assert color_family("ultraviolet-ish") is None


def test_color_similarity_orders_same_family_above_neutral_pairs():
    assert color_similarity(["camel"], ["tan"]) == 1.0
    assert color_similarity(["camel"], ["black"]) < 1.0
    assert color_similarity(["camel"], ["black"]) > color_similarity(["camel"], ["emerald"])


def test_silhouette_similarity():
    assert silhouette_similarity("oversized, relaxed", "relaxed boxy") > 0.7
    assert silhouette_similarity("slim fitted", "oversized") < 0.2
    assert silhouette_similarity(None, "slim") == 0.5


def test_subtype_detection():
    assert subtype("Light-wash denim jacket") == "jacket"
    assert subtype("Mid-wash straight jeans") == "jeans"
    assert subtype("gold hoop earrings") == "jewellery"


def test_exact_match_ranks_first_in_close_mode(wardrobe):
    cands = rank_candidates(analysis("insp_camel_work"), list(wardrobe.values()), StylePreferences(fidelity="close"))
    assert cands["outerwear-1"][0].garment_id == "s_camel_blazer"
    assert cands["bottom-1"][0].garment_id == "s_black_trousers"
    assert cands["shoes-1"][0].garment_id == "s_brown_loafers"
    for slot, cs in cands.items():
        assert all(c.garment_id in wardrobe for c in cs), slot
        assert all(0 <= c.score <= 1 for c in cs)


def test_candidates_respect_category_roles(wardrobe):
    cands = rank_candidates(analysis("insp_camel_work"), list(wardrobe.values()), StylePreferences())
    assert {wardrobe[c.garment_id].category for c in cands["shoes-1"]} == {"shoes"}
    assert {wardrobe[c.garment_id].category for c in cands["bottom-1"]} <= {"bottom", "dress"}


def test_accessory_needs_matching_type(wardrobe):
    cands = rank_candidates(
        analysis("insp_emerald_evening"), list(wardrobe.values()), StylePreferences(occasion="event")
    )
    assert cands["accessory-1"] == []  # a tote can't stand in for earrings


def test_exclusions_and_keep(wardrobe):
    prefs = StylePreferences(
        fidelity="close", exclude_garment_ids=["s_camel_blazer"], keep_garment_ids=["s_sage_blazer"]
    )
    cands = rank_candidates(analysis("insp_camel_work"), list(wardrobe.values()), prefs)
    ids = [c.garment_id for c in cands["outerwear-1"]]
    assert "s_camel_blazer" not in ids
    assert ids[0] == "s_sage_blazer"


def test_event_excludes_casual_garments(wardrobe):
    assert occasion_fit(wardrobe["s_white_sneakers"], "event") == "poor"
    assert occasion_fit(wardrobe["s_black_boots"], "event") == "good"
    cands = rank_candidates(
        analysis("insp_emerald_evening"), list(wardrobe.values()), StylePreferences(occasion="event")
    )
    assert "s_white_sneakers" not in [c.garment_id for c in cands["shoes-1"]]
    assert "s_denim_jacket" not in [c.garment_id for c in cands["outerwear-1"]]


def test_dress_slot_allows_two_piece_substitutes(wardrobe):
    cands = rank_candidates(
        analysis("insp_emerald_evening"),
        list(wardrobe.values()),
        StylePreferences(occasion="event", fidelity="creative"),
    )
    cats = {wardrobe[c.garment_id].category for c in cands["dress-1"]}
    assert "dress" in cats and cats & {"top", "bottom"}
