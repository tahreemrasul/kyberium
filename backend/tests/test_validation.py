from app.demo import SAMPLE_INSPIRATION_INDEX
from app.pipeline.composer import compose_with_rules
from app.pipeline.retrieval import rank_candidates
from app.pipeline.validation import build_look, build_looks
from app.schemas import ComposedGap, ComposedItem, ComposedLook, StylePreferences

CAMEL = SAMPLE_INSPIRATION_INDEX["insp_camel_work"]["analysis"]
EVENING = SAMPLE_INSPIRATION_INDEX["insp_emerald_evening"]["analysis"]


def item(gid, slot, text="works"):
    return ComposedItem(garment_id=gid, replaces_slot_id=slot, explanation=text)


def test_hallucinated_garment_is_removed_and_slot_becomes_gap(wardrobe):
    composed = ComposedLook(
        strategy="closest",
        title="T",
        items=[
            item("s_camel_blazer", "outerwear-1"),
            item("g_does_not_exist", "bottom-1"),
            item("s_white_tee", "top-1"),
        ],
    )
    look = build_look(composed, wardrobe, CAMEL, StylePreferences())
    assert [i.garment_id for i in look.items] == ["s_camel_blazer", "s_white_tee"]
    assert all(i.garment_id in wardrobe for i in look.items)
    assert "bottom-1" in {g.slot_id for g in look.gaps}
    assert any("isn't in your closet" in w for w in look.warnings)


def test_another_owners_garment_counts_as_hallucinated(wardrobe):
    mine = {k: v for k, v in wardrobe.items() if k != "s_camel_blazer"}
    look = build_look(
        ComposedLook(
            strategy="closest", title="T", items=[item("s_camel_blazer", "outerwear-1"), item("s_white_tee", "top-1")]
        ),
        mine,
        CAMEL,
        StylePreferences(),
    )
    assert "s_camel_blazer" not in [i.garment_id for i in look.items]


def test_duplicates_and_category_caps(wardrobe):
    composed = ComposedLook(
        strategy="closest",
        title="T",
        items=[
            item("s_black_trousers", "bottom-1"),
            item("s_black_trousers", "bottom-1"),
            item("s_ecru_trousers", "bottom-1"),
            item("s_wrap_dress", None),
        ],
    )
    look = build_look(composed, wardrobe, CAMEL, StylePreferences())
    assert [i.garment_id for i in look.items] == ["s_black_trousers"]


def test_exclusions_and_occasion_are_enforced(wardrobe):
    composed = ComposedLook(
        strategy="closest",
        title="T",
        items=[
            item("s_white_sneakers", "shoes-1"),
            item("s_black_cami", "dress-1"),
            item("s_satin_skirt", "dress-1"),
        ],
    )
    look = build_look(composed, wardrobe, EVENING, StylePreferences(occasion="event"))
    assert "s_white_sneakers" not in [i.garment_id for i in look.items]
    look = build_look(
        composed, wardrobe, EVENING, StylePreferences(occasion="everyday", exclude_garment_ids=["s_black_cami"])
    )
    assert "s_black_cami" not in [i.garment_id for i in look.items]


def test_impact_is_computed_server_side(wardrobe):
    composed = ComposedLook(
        strategy="closest",
        title="T",
        items=[
            item("s_camel_blazer", "outerwear-1"),
            item("s_white_tee", "top-1"),
            item("s_black_trousers", "bottom-1"),
            item("s_brown_loafers", "shoes-1"),
            item("s_tan_tote", "accessory-1"),
        ],
    )
    look = build_look(composed, wardrobe, CAMEL, StylePreferences())
    assert look.impact.owned_count == 5 and look.impact.gap_count == 0
    assert look.impact.purchase_needed is False
    assert "No new purchase needed" in look.impact.headline


def test_gaps_and_sourcing_hint_follow_shopping_preference(wardrobe):
    composed = ComposedLook(
        strategy="closest",
        title="T",
        items=[item("s_camel_blazer", "outerwear-1")],
        gaps=[ComposedGap(slot_id="bottom-1", reason="none", essential=True)],
    )
    look = build_look(composed, wardrobe, CAMEL, StylePreferences(shopping="wardrobe_first"))
    assert all(g.sourcing_hint is None for g in look.gaps)
    assert look.impact.purchase_needed is True
    look = build_look(composed, wardrobe, CAMEL, StylePreferences(shopping="secondhand_rental"))
    assert all(g.sourcing_hint and "pre-loved" in g.sourcing_hint for g in look.gaps)
    accessory_gap = next(g for g in look.gaps if g.slot_id == "accessory-1")
    assert accessory_gap.essential is False


def test_kept_garment_is_enforced(wardrobe):
    composed = ComposedLook(
        strategy="closest",
        title="T",
        items=[item("s_camel_blazer", "outerwear-1"), item("s_brown_loafers", "shoes-1")],
    )
    look = build_look(composed, wardrobe, CAMEL, StylePreferences(keep_garment_ids=["s_black_boots"]))
    ids = [i.garment_id for i in look.items]
    assert "s_black_boots" in ids and "s_brown_loafers" not in ids


def test_empty_or_all_invalid_look_is_dropped(wardrobe):
    assert (
        build_look(
            ComposedLook(strategy="closest", title="T", items=[item("nope", "top-1")]),
            wardrobe,
            CAMEL,
            StylePreferences(),
        )
        is None
    )


def test_build_looks_dedupes_identical_sets(wardrobe):
    a = ComposedLook(strategy="closest", title="A", items=[item("s_camel_blazer", "outerwear-1")])
    b = ComposedLook(strategy="creative", title="B", items=[item("s_camel_blazer", "outerwear-1")])
    assert len(build_looks([a, b], wardrobe, CAMEL, StylePreferences())) == 1


def test_rule_composer_never_uses_unowned_items(wardrobe):
    for sid, sample in SAMPLE_INSPIRATION_INDEX.items():
        prefs = StylePreferences(occasion=sample["analysis"].occasions[0])
        cands = rank_candidates(sample["analysis"], list(wardrobe.values()), prefs)
        looks = build_looks(
            compose_with_rules(sample["analysis"], prefs, cands, wardrobe).looks, wardrobe, sample["analysis"], prefs
        )
        assert looks, sid
        for lk in looks:
            assert all(i.garment_id in wardrobe for i in lk.items)
            covered = {i.replaces_slot_id for i in lk.items} | {g.slot_id for g in lk.gaps}
            assert covered >= {p.slot_id for p in sample["analysis"].pieces}


def test_rule_composer_reports_gap_when_role_missing(wardrobe):
    no_outer = {k: v for k, v in wardrobe.items() if v.category != "outerwear" and v.layer != "mid"}
    prefs = StylePreferences()
    cands = rank_candidates(CAMEL, list(no_outer.values()), prefs)
    looks = build_looks(compose_with_rules(CAMEL, prefs, cands, no_outer).looks, no_outer, CAMEL, prefs)
    gap = next(g for g in looks[0].gaps if g.slot_id == "outerwear-1")
    assert gap.essential and looks[0].impact.purchase_needed


def test_unlabelled_half_of_a_two_piece_is_attached_to_the_dress_slot(wardrobe):
    composed = ComposedLook(
        strategy="creative",
        title="Two-piece",
        items=[item("s_satin_skirt", "dress-1"), ComposedItem(garment_id="s_black_cami", explanation="x")],
    )
    look = build_look(composed, wardrobe, EVENING, StylePreferences(occasion="event"))
    cami = next(i for i in look.items if i.garment_id == "s_black_cami")
    assert cami.replaces_slot_id == "dress-1"
