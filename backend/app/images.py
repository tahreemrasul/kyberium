"""Upload validation and normalisation.

Only JPEG/PNG/WebP are accepted, verified by decoding (not by the declared
content type). Images are re-encoded as JPEG (max 1600px), which strips EXIF
metadata such as GPS location and bounds Gemini token cost.
"""

import hashlib
import io

from PIL import Image, ImageOps, UnidentifiedImageError

from app.errors import ApiError

Image.MAX_IMAGE_PIXELS = 40_000_000
_ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP", "MPO"}
MAX_SIDE = 1600


def normalize_image(data: bytes, max_bytes: int) -> tuple[bytes, str]:
    """Return (jpeg_bytes, sha256_of_original)."""
    if not data:
        raise ApiError(400, "empty_file", "The uploaded file is empty.")
    if len(data) > max_bytes:
        raise ApiError(413, "file_too_large", f"Images must be under {max_bytes // (1024 * 1024)} MB.")
    try:
        img = Image.open(io.BytesIO(data))
        fmt = img.format
        img.load()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise ApiError(415, "unsupported_image", "Please upload a JPEG, PNG or WebP image.") from exc
    if fmt not in _ALLOWED_FORMATS:
        raise ApiError(415, "unsupported_image", "Please upload a JPEG, PNG or WebP image.")

    img = ImageOps.exif_transpose(img)
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        bg = Image.new("RGB", img.size, (250, 247, 240))
        bg.paste(img, mask=img.split()[-1])
        img = bg
    else:
        img = img.convert("RGB")
    img.thumbnail((MAX_SIDE, MAX_SIDE))
    out = io.BytesIO()
    img.save(out, format="JPEG", quality=88, optimize=True)
    return out.getvalue(), hashlib.sha256(data).hexdigest()
