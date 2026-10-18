"""Standard-scale garment display images (no generative editing)."""

import io

from PIL import Image, ImageDraw

from app.pipeline.cutout import BACKGROUND, CANVAS, display_image, plain_background_mask


def jpeg(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()


def product_shot() -> Image.Image:
    img = Image.new("RGB", (600, 900), (244, 244, 244))  # plain studio backdrop
    ImageDraw.Draw(img).rectangle((180, 200, 420, 760), fill=(120, 30, 40))  # the garment
    return img


async def test_plain_backdrop_is_removed_and_scaled():
    png, method = await display_image(None, jpeg(product_shot()))
    out = Image.open(io.BytesIO(png)).convert("RGB")
    assert method == "cutout" and out.size == CANVAS
    assert out.getpixel((5, 5)) == BACKGROUND  # backdrop replaced by the studio cream
    assert out.getpixel((CANVAS[0] // 2, CANVAS[1] // 2))[0] > 90  # original garment pixels kept, centred


def test_busy_background_is_not_cut():
    busy = Image.effect_noise((400, 500), 90).convert("RGB")
    assert plain_background_mask(busy) is None


async def test_without_ai_busy_photos_are_padded_into_the_same_frame():
    busy = Image.effect_noise((300, 600), 90).convert("RGB")
    png, method = await display_image(None, jpeg(busy))
    assert method == "padded" and Image.open(io.BytesIO(png)).size == CANVAS
