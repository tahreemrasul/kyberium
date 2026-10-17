"""Regenerate the sample-wardrobe illustrations and inspiration boards.

Usage: uv run python scripts/render_assets.py
Garments are written as SVG. Inspirations are rasterised to PNG with headless
Chrome (set CHROME=/path/to/chrome if it isn't in the default macOS location),
because Gemini accepts raster images only.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.demo import ASSETS, SAMPLE_GARMENTS, SAMPLE_INSPIRATIONS  # noqa: E402
from app.demo.illustrations import composite_svg, garment_svg  # noqa: E402

CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")


def main() -> None:
    gdir, idir = ASSETS / "garments", ASSETS / "inspirations"
    gdir.mkdir(parents=True, exist_ok=True)
    idir.mkdir(parents=True, exist_ok=True)
    for g in SAMPLE_GARMENTS:
        art = g["art"]
        (gdir / f"{g['id']}.svg").write_text(
            garment_svg(art["shape"], art["color"], art.get("accent"), art.get("stripes"), title=g["name"])
        )
    print(f"wrote {len(SAMPLE_GARMENTS)} garment svgs")

    # Raster copies for the multimodal critic (Gemini does not accept SVG).
    pdir = ASSETS / "garments_png"
    pdir.mkdir(exist_ok=True)
    for g in SAMPLE_GARMENTS:
        subprocess.run(
            [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--screenshot={pdir / (g['id'] + '.png')}",
             "--window-size=400,500", f"file://{gdir / (g['id'] + '.svg')}"],
            check=True, capture_output=True,
        )
    print(f"wrote {len(SAMPLE_GARMENTS)} garment pngs")

    with tempfile.TemporaryDirectory() as tmp:
        for insp in SAMPLE_INSPIRATIONS:
            svg = composite_svg(insp["placements"])
            html = Path(tmp) / f"{insp['id']}.html"
            html.write_text(f"<html><body style='margin:0'>{svg}</body></html>")
            out = idir / f"{insp['id']}.png"
            subprocess.run(
                [
                    CHROME,
                    "--headless=new",
                    "--disable-gpu",
                    "--hide-scrollbars",
                    f"--screenshot={out}",
                    "--window-size=900,1100",
                    f"file://{html}",
                ],
                check=True,
                capture_output=True,
            )
            print("wrote", out.name)


if __name__ == "__main__":
    main()
