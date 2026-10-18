"""Demo fixtures: sample wardrobe, illustrated inspirations and their cached analyses."""

from datetime import UTC, datetime, timedelta
from pathlib import Path

from app.demo.catalog import SAMPLE_GARMENT_IDS, SAMPLE_GARMENTS, SAMPLE_INSPIRATION_INDEX, SAMPLE_INSPIRATIONS
from app.schemas import Garment

ASSETS = Path(__file__).parent / "assets"


def sample_garment_image_url(gid: str) -> str:
    return f"/media/samples/garments/{gid}.svg"


def sample_inspiration_image_url(iid: str) -> str:
    return f"/media/samples/inspirations/{iid}.png"


def sample_garments(now: datetime | None = None) -> list[Garment]:
    now = now or datetime.now(UTC)
    out = []
    for i, spec in enumerate(SAMPLE_GARMENTS):
        attrs = {k: v for k, v in spec.items() if k != "art"}
        ts = now - timedelta(seconds=i)  # keep catalogue order stable in the gallery
        out.append(
            Garment(
                **attrs,
                image_url=sample_garment_image_url(spec["id"]),
                image_kind="illustration",
                source="sample",
                verified_by_user=True,
                created_at=ts,
                updated_at=ts,
            )
        )
    return out


__all__ = [
    "ASSETS",
    "SAMPLE_GARMENTS",
    "SAMPLE_GARMENT_IDS",
    "SAMPLE_INSPIRATIONS",
    "SAMPLE_INSPIRATION_INDEX",
    "sample_garment_image_url",
    "sample_garments",
    "sample_inspiration_image_url",
]
