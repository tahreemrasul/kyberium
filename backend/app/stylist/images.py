"""Load garment/inspiration images for the multimodal critic, downscaled to bound token cost."""

import io
import logging
import re
from collections.abc import Awaitable, Callable

from PIL import Image

from app.demo import ASSETS
from app.storage import BlobStore

log = logging.getLogger("rewear.stylist")

ImageLoader = Callable[[str], Awaitable[tuple[bytes, str] | None]]
MAX_SIDE = 384

_SAMPLE = re.compile(r"^/media/samples/(garments|inspirations)/([A-Za-z0-9_-]+)\.(svg|png)$")
_BLOB = re.compile(r"^/media/((?:uploads|inspirations)/[A-Za-z0-9_-]+/[A-Za-z0-9_-]+\.(?:jpg|png|webp))$")


def _shrink(data: bytes) -> bytes:
    img = Image.open(io.BytesIO(data)).convert("RGB")
    img.thumbnail((MAX_SIDE, MAX_SIDE))
    out = io.BytesIO()
    img.save(out, format="JPEG", quality=82)
    return out.getvalue()


def make_image_loader(blobs: BlobStore | None) -> ImageLoader:
    async def load(url: str) -> tuple[bytes, str] | None:
        try:
            if m := _SAMPLE.match(url):
                folder, name, _ = m.groups()
                path = ASSETS / ("garments_png" if folder == "garments" else folder) / f"{name}.png"
                return (_shrink(path.read_bytes()), "image/jpeg") if path.is_file() else None
            if (m := _BLOB.match(url)) and blobs is not None:
                blob = await blobs.get(m.group(1))
                return (_shrink(blob[0]), "image/jpeg") if blob else None
        except Exception as exc:  # an image is a nice-to-have for the critic, never a failure
            log.warning("could not load image %s: %s", url, exc)
        return None

    return load
