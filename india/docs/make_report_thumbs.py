#!/usr/bin/env python3
"""Render the imagery the delivery report needs, from the production collection.

Two families, both written into `<out>/img/`:

  <CELL>_<YEAR>.jpg   six sample cells, 560 px
  india_<YEAR>.jpg    the whole country, one tile per phenological year, 450x480

Both use the same stretch, so the tiles are comparable to each other and to the
ones already in the report.  See `docs/REPORT.md` for the content contract.

    cd india && source .venv/bin/activate
    python docs/make_report_thumbs.py --out /tmp/report
    python docs/make_report_thumbs.py --coverage 2018   # just measure, render nothing

Needs Earth Engine: `earthengine authenticate` once.
"""

import argparse
import math
import pathlib
import time
import urllib.request

import ee

COLLECTION = "projects/mapbiomas-mosaics/assets/LANDSAT/LULC/INDIA/mosaics-2"
PROJECT = "mapbiomas-mosaics"

# The one stretch, shared by every image in the report. Same values as
# docs/visualize_stuck_mosaics.js. Do not fork this: tiles rendered under
# different parameters cannot be compared, which is the whole point of the grid.
VIS = dict(bands=["red_median", "green_median", "blue_median"], min=0, max=4000, gamma=1.3)

# Fixed extent for the national grid, so all forty tiles line up.
# From col.filter(year=2018).geometry().bounds().
NATIONAL_REGION = [67.5, 6.0, 97.5, 38.0]

YEARS = range(1986, 2026)

# Six interior cells, all above 99% valid pixels, spread across the country.
# Coastal cells look broken in a gallery — the region mask clips most of the
# frame — so they are chosen by measured coverage, never by eye. Re-pick with
# --coverage if the set ever needs to change.
SAMPLE_CELLS = [
    "NG-42-X-B_2015",  # Thar desert, north-west
    "NG-43-X-D_2017",  # central plateau, the 250-granule cell from the incident
    "NH-44-V-C_2019",  # Himalayan front, high relief
    "NF-45-Y-B_2018",  # eastern plateau
    "NC-43-Z-B_2018",  # southern peninsula
    "NG-46-X-B_2018",  # far north-east
]


def fetch(url: str, dest: pathlib.Path, tries: int = 4) -> int:
    """Download a thumbnail, retrying: getThumbURL is occasionally flaky."""
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=600) as response:
                data = response.read()
            if len(data) < 800:
                raise RuntimeError("suspiciously small response: %d bytes" % len(data))
            dest.write_bytes(data)
            return len(data)
        except Exception:
            if attempt == tries - 1:
                raise
            time.sleep(4 * (attempt + 1))
    raise AssertionError("unreachable")


def coverage(year: int) -> list[tuple[str, float, float, float]]:
    """Valid-pixel fraction per cell for one year, plus each cell's centroid.

    This is how the sample cells get chosen. A cell on the coast or on a border
    delivers only the part inside the classification regions, so its frame is
    mostly empty even though the mosaic is perfectly good.
    """
    col = ee.ImageCollection(COLLECTION).filter(ee.Filter.eq("year", year))

    def stat(img):
        geom = img.geometry()
        frac = img.select("red_median").mask().reduceRegion(
            reducer=ee.Reducer.mean(), geometry=geom, scale=2000, maxPixels=1e9, bestEffort=True)
        centroid = geom.centroid(1000).coordinates()
        return ee.Feature(None, {
            "id": img.get("system:index"),
            "cov": frac.get("red_median"),
            "lon": centroid.get(0),
            "lat": centroid.get(1),
        })

    rows = col.map(stat).reduceColumns(
        ee.Reducer.toList(4), ["id", "cov", "lon", "lat"]).get("list").getInfo()
    return sorted(((r[0], r[1], r[2], r[3]) for r in rows if r[1] is not None), key=lambda r: -r[1])


def pick_spread(rows, keep, n, floor=0.99):
    """Greedy farthest-point pick among cells above `floor`, away from `keep`."""
    pool = [r for r in rows if r[1] >= floor]
    chosen = list(keep)
    out = []
    for _ in range(n):
        best = max(pool, key=lambda r: (
            min(math.hypot(r[2] - c[2], r[3] - c[3]) for c in chosen)
            if r[0] not in {c[0] for c in chosen} else -1))
        chosen.append(best)
        out.append(best)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=pathlib.Path, help="directory to write img/ into")
    ap.add_argument("--coverage", type=int, metavar="YEAR",
                    help="print valid-pixel coverage per cell for a year and exit")
    ap.add_argument("--force", action="store_true", help="re-render tiles that already exist")
    args = ap.parse_args()

    ee.Initialize(project=PROJECT)

    if args.coverage:
        rows = coverage(args.coverage)
        print("%d cells, %d at or above 99.5%%" % (len(rows), sum(1 for r in rows if r[1] >= 0.995)))
        for cid, cov, lon, lat in rows:
            print("  %-16s cov=%.4f  lon=%7.2f  lat=%6.2f" % (cid, cov, lon, lat))
        return

    if not args.out:
        ap.error("--out is required unless --coverage is given")

    img_dir = args.out / "img"
    img_dir.mkdir(parents=True, exist_ok=True)

    for cell in SAMPLE_CELLS:
        dest = img_dir / (cell + ".jpg")
        if dest.exists() and dest.stat().st_size > 2000 and not args.force:
            print("cell %-16s (kept)" % cell, flush=True)
            continue
        image = ee.Image(COLLECTION + "/" + cell)
        url = image.getThumbURL(dict(VIS, dimensions=560, region=image.geometry(), format="jpg"))
        print("cell %-16s %8d bytes" % (cell, fetch(url, dest)), flush=True)

    col = ee.ImageCollection(COLLECTION)
    region = ee.Geometry.Rectangle(NATIONAL_REGION, None, False)
    for year in YEARS:
        dest = img_dir / ("india_%d.jpg" % year)
        if dest.exists() and dest.stat().st_size > 2000 and not args.force:
            print("year %d  (kept)" % year, flush=True)
            continue
        mosaic = col.filter(ee.Filter.eq("year", year)).mosaic()
        url = mosaic.getThumbURL(dict(VIS, dimensions=480, region=region, format="jpg"))
        print("year %d  %8d bytes" % (year, fetch(url, dest)), flush=True)

    total = sum(p.stat().st_size for p in img_dir.glob("*.jpg"))
    print("done — %d files, %.2f MB" % (len(list(img_dir.glob('*.jpg'))), total / 1e6))


if __name__ == "__main__":
    main()
