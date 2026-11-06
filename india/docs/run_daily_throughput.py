#!/usr/bin/env python3
"""Day-by-day record of the production run, read from the delivered assets.

`listOperations` is the obvious source and the wrong one: it has a ceiling and
drops old operations, so it under-counts a run this long.  The assets do not —
every delivered image carries both timestamps we need:

  updateTime              when Earth Engine finished writing the asset  (completed)
  properties.built_utc    when the pipeline composed and submitted the export

Counting by `updateTime` gives throughput.  The gap between the two is queue
lag, which is what the stall incident was really about, so both are kept.

    cd india && source .venv/bin/activate
    python docs/run_daily_throughput.py                    # writes docs/run_daily_throughput.csv
    python docs/run_daily_throughput.py --out /tmp/x.csv

Output columns: date, completed, submitted, gb_written, scenes, cumulative.
"""

import argparse
import collections
import csv
import datetime as dt
import pathlib
import sys

import ee

COLLECTION = "projects/mapbiomas-mosaics/assets/LANDSAT/LULC/INDIA/mosaics-2"
PROJECT = "mapbiomas-mosaics"
PAGE = 500


def parse_ts(value):
    """RFC-3339 from the EE API, with or without fractional seconds."""
    if not value:
        return None
    value = value.replace("Z", "+00:00")
    try:
        return dt.datetime.fromisoformat(value)
    except ValueError:
        head, _, rest = value.partition(".")
        offset = rest[rest.find("+"):] if "+" in rest else "+00:00"
        return dt.datetime.fromisoformat(head + offset)


def collect():
    """Every asset in the collection, as (completed_day, submitted_day, bytes, scenes)."""
    rows = []
    token = None
    page = 0
    while True:
        request = {"parent": COLLECTION, "pageSize": PAGE}
        if token:
            request["pageToken"] = token
        response = ee.data.listAssets(request)
        for asset in response.get("assets", []):
            props = asset.get("properties") or {}
            completed = parse_ts(asset.get("updateTime"))
            submitted = parse_ts(props.get("built_utc"))
            rows.append((
                completed.date() if completed else None,
                submitted.date() if submitted else None,
                int(asset.get("sizeBytes") or 0),
                int(props.get("n_scenes") or 0),
            ))
        page += 1
        print("  page %d — %d assets so far" % (page, len(rows)), file=sys.stderr, flush=True)
        token = response.get("nextPageToken")
        if not token:
            return rows


def main() -> None:
    here = pathlib.Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=pathlib.Path, default=here / "run_daily_throughput.csv")
    args = ap.parse_args()

    ee.Initialize(project=PROJECT)
    rows = collect()

    done = collections.Counter()
    sent = collections.Counter()
    size = collections.Counter()
    scenes = collections.Counter()
    for completed, submitted, nbytes, nscenes in rows:
        if completed:
            done[completed] += 1
            size[completed] += nbytes
            scenes[completed] += nscenes
        if submitted:
            sent[submitted] += 1

    days = sorted(set(done) | set(sent))
    if not days:
        raise SystemExit("no dated assets found")

    span = [days[0] + dt.timedelta(days=i) for i in range((days[-1] - days[0]).days + 1)]
    running = 0
    with args.out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["date", "completed", "submitted", "gb_written", "scenes", "cumulative"])
        for day in span:
            running += done[day]
            writer.writerow([day.isoformat(), done[day], sent[day],
                             round(size[day] / 1e9, 2), scenes[day], running])

    active = [d for d in span if done[d]]
    peak = max(span, key=lambda d: done[d])
    print("assets            %d" % len(rows))
    print("calendar span     %s .. %s  (%d days)" % (days[0], days[-1], len(span)))
    print("days with output  %d" % len(active))
    print("peak day          %s — %d mosaics" % (peak, done[peak]))
    print("median active day %d mosaics" % sorted(done[d] for d in active)[len(active) // 2])
    print("total written     %.2f TB" % (sum(size.values()) / 1e12))
    print("wrote %s" % args.out)


if __name__ == "__main__":
    main()
