"""Image serving.

Uploaded images live under unguessable keys (owner hash + random id) and are
served as capability URLs so plain <img> tags work without auth headers.
Sample illustrations are served from the package.
"""

import re

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from app.demo import ASSETS
from app.deps import blobs_dep
from app.errors import not_found
from app.storage import BlobStore

router = APIRouter(tags=["media"])
_NAME = re.compile(r"^[A-Za-z0-9_-]{1,64}\.(svg|png|jpg)$")
_TYPES = {"svg": "image/svg+xml", "png": "image/png", "jpg": "image/jpeg"}
_CACHE = {"Cache-Control": "public, max-age=31536000, immutable", "X-Content-Type-Options": "nosniff"}


@router.get("/media/{kind}/{folder}/{name}")
async def media(kind: str, folder: str, name: str, blobs: BlobStore = Depends(blobs_dep)) -> Response:
    if not _NAME.match(name):
        raise not_found("Image")
    if kind == "samples":
        if folder not in ("garments", "inspirations"):
            raise not_found("Image")
        path = ASSETS / folder / name
        if not path.is_file():
            raise not_found("Image")
        headers = {**_CACHE, "Cache-Control": "public, max-age=3600"}
        if name.endswith(".svg"):
            headers["Content-Security-Policy"] = "default-src 'none'; style-src 'unsafe-inline'"
        return Response(path.read_bytes(), media_type=_TYPES[name.rsplit(".", 1)[1]], headers=headers)
    if kind not in ("uploads", "inspirations"):
        raise not_found("Image")
    try:
        blob = await blobs.get(f"{kind}/{folder}/{name}")
    except ValueError:
        blob = None
    if blob is None:
        raise not_found("Image")
    data, ct = blob
    return Response(data, media_type=ct, headers=_CACHE)
