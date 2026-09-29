"""
Canonical status report for the India mosaic production run.

One command, one fixed format, so the report reads the same every time it
is run. Read-only: it lists assets and operations, queues nothing, changes
nothing. Safe at any time, from a terminal or a notebook.

Usage:

    python scripts/monitor_status.py                # production collection
    python scripts/monitor_status.py --collection projects/.../mosaics-2
    python scripts/monitor_status.py --hours 6      # throughput window

The report answers, in order:
    1. DONE        how many mosaics are finished and sitting in the collection
    2. IN FLIGHT    how many tasks are RUNNING / PENDING right now
    3. THROUGHPUT   mosaics finished per hour, over the last N hours
    4. ETA          remaining / throughput
    5. SPACE        asset-root quota, used vs free
    6. STRAGGLERS   RUNNING tasks past the stuck threshold (default 8h)
"""

import argparse
import re
import sys
from collections import Counter
from datetime import datetime, timezone, timedelta

sys.path.insert(0, '/Users/joaosiqueira/Documents/Projects/countries-mosaics/india')

import ee
from pipeline import config as C

GRID = 'data/vectors/grid_cells_india.geojson'
PAT = re.compile(r'^[A-Z]{2}-\d{2}-[A-Z]-[A-Z]_\d{4}$')
STUCK_HOURS = 8.0


def _ts(x):
    if not x or str(x).startswith('1970'):
        return None
    try:
        return datetime.fromisoformat(str(x).replace('Z', '+00:00'))
    except Exception:
        return None


def report(collection_path, hours, stuck_hours):
    ee.Initialize(project='mapbiomas-mosaics')
    now = datetime.now(timezone.utc)

    # --- 1. DONE (collection) ---------------------------------------------
    assets = ee.data.listAssets({'parent': collection_path}).get('assets', [])
    done = {a['id'].rsplit('/', 1)[-1] for a in assets
            if PAT.match(a['id'].rsplit('/', 1)[-1])}
    total = 283 * 40  # 283 cells x 1986..2025
    pct = 100.0 * len(done) / total if total else 0.0

    # --- 2. IN FLIGHT -------------------------------------------------------
    ops = ee.data.listOperations(project='projects/mapbiomas-mosaics')

    def desc(o):
        return o.get('metadata', {}).get('description', '')

    def state(o):
        return o.get('metadata', {}).get('state')

    clean = re.compile(r'^[A-Z]{2}_\d{2}_[A-Z]_[A-Z]_\d{4}$')
    running = sum(1 for o in ops if state(o) == 'RUNNING' and clean.match(desc(o)))
    pending = sum(1 for o in ops if state(o) == 'PENDING' and clean.match(desc(o)))
    failed = sum(1 for o in ops if state(o) == 'FAILED' and clean.match(desc(o)))

    # --- 3. THROUGHPUT ------------------------------------------------------
    by_hour = Counter()
    for o in ops:
        if state(o) == 'SUCCEEDED' and clean.match(desc(o)):
            e = _ts(o.get('metadata', {}).get('endTime'))
            if e and e > now - timedelta(hours=hours):
                by_hour[e.strftime('%d %H:00')] += 1
    recent = [n for _, n in sorted(by_hour.items())[-4:]]
    avg = sum(recent) / len(recent) if recent else 0.0

    # --- 4. ETA -------------------------------------------------------------
    remaining = total - len(done)
    eta_h = remaining / avg if avg else float('inf')

    # --- 5. SPACE -----------------------------------------------------------
    q = ee.data.getAssetRootQuota('projects/mapbiomas-mosaics/assets')
    limit = q['asset_size']['limit']
    use = q['asset_size']['usage']

    # --- 6. STRAGGLERS -------------------------------------------------------
    stragglers = []
    for o in ops:
        md = o.get('metadata', {})
        if state(o) == 'RUNNING' and clean.match(desc(o)):
            s = _ts(md.get('startTime'))
            if s and (now - s).total_seconds() > stuck_hours * 3600:
                stragglers.append((desc(o), (now - s).total_seconds() / 3600))
    stragglers.sort(key=lambda x: -x[1])

    # --- print ---------------------------------------------------------------
    print('agora (UTC): {}'.format(now.strftime('%Y-%m-%d %H:%M')))
    print()
    print('=== TAREFAS ===')
    print('done: {} | running: {} | pending: {} | failed: {}'.format(
        len(done), running, pending, failed))
    print('progresso: {:.1f}%'.format(pct))
    print('SUCCEEDED/h (últimas {}h): {}'.format(hours, dict(sorted(by_hour.items()))))
    print('média últimas 4h: {:.0f}/h'.format(avg))
    print('restante a concluir: {} mosaicos'.format(remaining))
    if avg:
        print('ETA (a {:.0f}/h): {:.0f}h = {:.1f} dias'.format(avg, eta_h, eta_h / 24))
    print()
    print('=== ESPAÇO ===')
    print('uso: {:.2f} TB / {:.2f} TB | livre: {:.2f} GB'.format(
        use / 1e12, limit / 1e12, (limit - use) / 1e9))
    print()
    print('=== TRAVADOS (>{}h) ==='.format(stuck_hours))
    if stragglers:
        for d, h in stragglers:
            print('  {:22s} {:.1f}h'.format(d, h))
    else:
        print('  nenhum')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--collection', default=C.PRODUCTION_COLLECTION)
    ap.add_argument('--hours', type=int, default=6)
    ap.add_argument('--stuck-hours', type=float, default=STUCK_HOURS)
    args = ap.parse_args()
    report(args.collection, args.hours, args.stuck_hours)


if __name__ == '__main__':
    main()
