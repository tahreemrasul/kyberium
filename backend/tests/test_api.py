from tests.conftest import FakeAI, image_bytes

DRAFT = {
    "name": "Olive overshirt",
    "category": "outerwear",
    "subcategory": "overshirt",
    "colors": ["olive"],
    "silhouette": "boxy",
    "formality": "casual",
    "layer": "outer",
    "style_tags": ["utility"],
    "occasions": ["everyday"],
    "is_garment": True,
}


def test_health_and_session(client):
    assert client.get("/health").json()["status"] == "ok"
    token = client.post("/session").json()["token"]
    assert token.startswith("rw_")


def test_auth_required(client):
    r = client.get("/wardrobe/items")
    assert r.status_code == 401 and r.json()["error"]["code"] == "unauthorized"
    r = client.get("/wardrobe/items", headers={"Authorization": "Bearer ../../etc"})
    assert r.status_code == 401


def test_sample_wardrobe_load_is_idempotent_and_keeps_uploads(client, auth):
    h = auth()
    assert client.post("/demo/wardrobe", headers=h).json()["added"] == 20
    assert client.post("/demo/wardrobe", headers=h).json()["added"] == 0
    up = client.post("/wardrobe/items/analyze", headers=h, files={"file": ("a.png", image_bytes(), "image/png")}).json()
    client.post("/wardrobe/items", headers=h, json={**DRAFT, "upload_id": up["upload_id"]})
    left = client.delete("/demo/wardrobe", headers=h).json()["items"]
    assert [g["source"] for g in left] == ["upload"]


def test_upload_validation(client, auth):
    h = auth()
    r = client.post("/wardrobe/items/analyze", headers=h, files={"file": ("x.png", b"not an image", "image/png")})
    assert r.status_code == 415 and r.json()["error"]["code"] == "unsupported_image"
    r = client.post("/wardrobe/items/analyze", headers=h, files={"file": ("x.gif", image_bytes("GIF"), "image/gif")})
    assert r.status_code == 415
    big = b"\xff\xd8" + b"0" * (9 * 1024 * 1024)
    r = client.post("/wardrobe/items/analyze", headers=h, files={"file": ("x.jpg", big, "image/jpeg")})
    assert r.status_code == 413


def test_upload_without_ai_returns_manual_draft(client, auth):
    h = auth()
    r = client.post("/wardrobe/items/analyze", headers=h, files={"file": ("a.jpg", image_bytes("JPEG"), "image/jpeg")})
    body = r.json()
    assert r.status_code == 200 and body["draft"] is None and body["engine"] == "none"
    assert client.get(body["image_url"]).status_code == 200


def test_upload_tag_confirm_edit_delete_with_ai(client, auth):
    client.state["ai"] = FakeAI({"GarmentDraft": DRAFT})
    h = auth()
    first = client.post(
        "/wardrobe/items/analyze", headers=h, files={"file": ("a.png", image_bytes(), "image/png")}
    ).json()
    assert first["engine"] == "gemini" and first["draft"]["category"] == "outerwear" and not first["cached"]
    again = client.post("/wardrobe/items/analyze", headers=h, files={"file": ("a.png", image_bytes(), "image/png")})
    assert again.json()["cached"] is True  # same image is not re-analysed
    assert [c["schema"] for c in client.state["ai"].calls].count("GarmentDraft") == 1
    assert first["display_url"].endswith("_cut.png") and client.get(first["display_url"]).status_code == 200

    created = client.post(
        "/wardrobe/items", headers=h, json={**DRAFT, "name": "My overshirt", "upload_id": first["upload_id"]}
    )
    assert created.status_code == 201
    gid = created.json()["id"]
    dup = client.post("/wardrobe/items", headers=h, json={**DRAFT, "upload_id": first["upload_id"]})
    assert dup.status_code == 409

    patched = client.patch(f"/wardrobe/items/{gid}", headers=h, json={"colors": ["Khaki", "khaki"], "name": None})
    assert patched.json()["colors"] == ["khaki"] and patched.json()["name"] == "My overshirt"
    bad = client.patch(f"/wardrobe/items/{gid}", headers=h, json={"category": "spaceship"})
    assert bad.status_code == 422 and bad.json()["error"]["code"] == "invalid_request"

    assert client.delete(f"/wardrobe/items/{gid}", headers=h).status_code == 204
    assert client.get("/wardrobe/items", headers=h).json() == []
    assert client.get(first["image_url"]).status_code == 404


def test_owner_isolation(client, auth):
    alice, bob = auth(), auth()
    client.post("/demo/wardrobe", headers=alice)
    up = client.post("/wardrobe/items/analyze", headers=alice, files={"file": ("a.png", image_bytes(), "image/png")})
    upload_id = up.json()["upload_id"]
    gid = client.post("/wardrobe/items", headers=alice, json={**DRAFT, "upload_id": upload_id}).json()["id"]

    assert client.get("/wardrobe/items", headers=bob).json() == []
    assert client.patch(f"/wardrobe/items/{gid}", headers=bob, json={"name": "mine"}).status_code == 404
    assert client.delete(f"/wardrobe/items/{gid}", headers=bob).status_code == 404
    # Bob cannot attach Alice's upload to his closet.
    assert client.post("/wardrobe/items", headers=bob, json={**DRAFT, "upload_id": upload_id}).status_code == 404

    # Bob's styling never sees Alice's garments, and he can't swap one in.
    client.post("/demo/wardrobe", headers=bob)
    client.delete("/wardrobe/items/s_camel_blazer", headers=bob)
    insp = client.post("/inspirations", headers=bob, data={"sample_id": "insp_camel_work"}).json()
    gen = client.post("/looks/generate", headers=bob, json={"inspiration_id": insp["id"]}).json()
    used = {i["garment_id"] for lk in gen["looks"] for i in lk["items"]}
    assert "s_camel_blazer" not in used and gid not in used
    look = gen["looks"][0]
    outer = next(i for i in look["items"] if i["garment"]["category"] == "outerwear")
    r = client.post(
        "/looks/swap",
        headers=bob,
        json={
            "generation_id": gen["id"],
            "look_id": look["id"],
            "old_garment_id": outer["garment_id"],
            "new_garment_id": gid,
        },
    )
    assert r.status_code == 400
    # Alice can't read Bob's generation.
    assert client.get(f"/looks/generations/{gen['id']}", headers=alice).status_code == 404


def test_full_styling_journey(client, auth):
    h = auth()
    insp = client.post("/inspirations", headers=h, data={"sample_id": "insp_trench_travel"}).json()
    r = client.post("/looks/generate", headers=h, json={"inspiration_id": insp["id"]})
    assert r.status_code == 409 and r.json()["error"]["code"] == "empty_wardrobe"

    client.post("/demo/wardrobe", headers=h)
    prefs = {"occasion": "travel", "fidelity": "close", "shopping": "secondhand_rental"}
    gen = client.post("/looks/generate", headers=h, json={"inspiration_id": insp["id"], "preferences": prefs}).json()
    assert gen["engine"] == "rules" and "Demo mode" in gen["engine_note"]
    look = gen["looks"][0]
    assert look["strategy"] == "closest"
    hat = next(g for g in look["gaps"] if g["slot_id"] == "accessory-1")
    assert hat["essential"] is False and "pre-loved" in hat["sourcing_hint"]

    # Swap shoes for another owned pair.
    shoes = next(i for i in look["items"] if i["garment"]["category"] == "shoes")
    alt = "s_brown_loafers" if shoes["garment_id"] != "s_brown_loafers" else "s_black_boots"
    swapped = client.post(
        "/looks/swap",
        headers=h,
        json={
            "generation_id": gen["id"],
            "look_id": look["id"],
            "old_garment_id": shoes["garment_id"],
            "new_garment_id": alt,
        },
    )
    assert swapped.status_code == 200
    new_look = swapped.json()["looks"][0]
    assert alt in [i["garment_id"] for i in new_look["items"]]
    bad = client.post(
        "/looks/swap",
        headers=h,
        json={
            "generation_id": gen["id"],
            "look_id": look["id"],
            "old_garment_id": alt,
            "new_garment_id": "s_ecru_trousers",
        },
    )
    assert bad.status_code == 400

    bottom = next(i for i in new_look["items"] if i["garment"]["category"] == "bottom")["garment_id"]
    refined = client.post(
        "/looks/refine",
        headers=h,
        json={
            "generation_id": gen["id"],
            "look_id": look["id"],
            "instruction": "Keep the shoes but change the trousers",
        },
    )
    refined = refined.json()
    assert bottom in refined["preferences"]["exclude_garment_ids"]
    assert alt in refined["preferences"]["keep_garment_ids"]
    assert all(i["garment_id"] != bottom for lk in refined["looks"] for i in lk["items"])
    assert alt in [i["garment_id"] for i in refined["looks"][0]["items"]]

    saved = client.post(
        "/looks/saved", headers=h, json={"generation_id": refined["id"], "look_id": refined["looks"][0]["id"]}
    )
    assert saved.status_code == 201
    assert len(client.get("/looks/saved", headers=h).json()) == 1
    assert client.delete(f"/looks/saved/{saved.json()['id']}", headers=h).status_code == 204


def test_live_inspiration_requires_ai(client, auth):
    h = auth()
    r = client.post("/inspirations", headers=h, files={"file": ("i.png", image_bytes(), "image/png")})
    assert r.status_code == 503 and r.json()["error"]["code"] == "ai_unavailable"
    assert client.post("/inspirations", headers=h).status_code == 400


def test_live_inspiration_with_ai(client, auth):
    analysis = {
        "is_outfit": True,
        "summary": "s",
        "formality": "casual",
        "occasions": ["everyday"],
        "pieces": [
            {"slot_id": "x", "category": "top", "description": "Tee", "formality": "casual"},
            {"slot_id": "x", "category": "top", "description": "Cardigan", "formality": "casual"},
        ],
    }
    client.state["ai"] = FakeAI({"InspirationAnalysis": analysis})
    h = auth()
    r = client.post("/inspirations", headers=h, files={"file": ("i.png", image_bytes(), "image/png")})
    assert r.status_code == 201
    assert [p["slot_id"] for p in r.json()["analysis"]["pieces"]] == ["top-1", "top-2"]


def test_media_rejects_traversal(client):
    assert client.get("/media/samples/garments/..%2F..%2Fconfig.py").status_code == 404
    assert client.get("/media/secrets/a/b.jpg").status_code == 404
    assert client.get("/media/samples/garments/s_camel_blazer.svg").headers["content-type"].startswith("image/svg")
