#!/usr/bin/env python3
from __future__ import annotations
import csv
import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

AUDIT_REPO = Path('/home/chuck/repos/ebay-mitchell-inventory-auditor')
DASH_REPO = Path('/home/chuck/repos/mitchell-dashboard')
STATE_DIR = Path('/home/chuck/.openclaw/workspace/state')
STATE_PATH = STATE_DIR / 'mitchell_weekly_snapshot.json'
PUBLISH_CMD = ['/home/chuck/bin/publish_static_app.sh', 'mitchell-dashboard', str(DASH_REPO / 'web')]
LIVE_CMD = ['/usr/bin/python3', str(AUDIT_REPO / 'scripts' / 'generate_live_outputs.py')]
BUILD_CMD = ['/usr/bin/python3', str(DASH_REPO / 'scripts' / 'build_dashboard_data.py')]
URL = 'https://mitchell-dashboard.openclawchuck.com'


def run(cmd, cwd=None):
    proc = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    return proc


def read_csv(path: Path):
    with path.open(newline='') as handle:
        return list(csv.DictReader(handle))


def build_snapshot(run_dir: Path, dashboard_path: Path):
    data = json.loads(dashboard_path.read_text())
    overlaps = read_csv(run_dir / 'overlaps.csv')
    warnings = read_csv(run_dir / 'warnings.csv')
    available_parts = data.get('available_parts', [])

    overlap_parts = sorted({row['part_number'] for row in overlaps if row.get('part_number')})
    warning_signatures = sorted({
        f"{row.get('listing_id','')}|{row.get('part_number','')}|{row.get('warning_type','')}|{row.get('warning_detail','')}"
        for row in warnings
    })
    price_mismatch_parts = sorted({
        row.get('part_number') for row in available_parts
        if row.get('price_mismatch') and row.get('part_number')
    })
    warning_type_counts = Counter(row.get('warning_type') or 'unknown' for row in warnings)

    return {
        'run_name': data.get('run_name'),
        'data_source_note': data.get('data_source_note'),
        'requested_listing_count': data.get('scope', {}).get('requested_listing_count'),
        'successful_listing_count': data.get('run_status', {}).get('successful_listing_count'),
        'failed_listing_count': data.get('run_status', {}).get('failed_listing_count'),
        'summary': data.get('summary', {}),
        'available_summary': data.get('available_summary', {}),
        'overlap_parts': overlap_parts,
        'warning_signatures': warning_signatures,
        'price_mismatch_parts': price_mismatch_parts,
        'warning_type_counts': dict(warning_type_counts),
    }


def diff_snapshot(prev, curr):
    if not prev:
        return {
            'first_run': True,
            'new_overlap_parts': curr['overlap_parts'][:10],
            'new_price_mismatch_parts': curr['price_mismatch_parts'][:10],
            'new_warning_count': len(curr['warning_signatures']),
        }
    prev_overlap = set(prev.get('overlap_parts', []))
    prev_price = set(prev.get('price_mismatch_parts', []))
    prev_warn = set(prev.get('warning_signatures', []))
    curr_overlap = set(curr.get('overlap_parts', []))
    curr_price = set(curr.get('price_mismatch_parts', []))
    curr_warn = set(curr.get('warning_signatures', []))
    return {
        'first_run': False,
        'new_overlap_parts': sorted(curr_overlap - prev_overlap),
        'resolved_overlap_parts': sorted(prev_overlap - curr_overlap),
        'new_price_mismatch_parts': sorted(curr_price - prev_price),
        'resolved_price_mismatch_parts': sorted(prev_price - curr_price),
        'new_warning_count': len(curr_warn - prev_warn),
        'resolved_warning_count': len(prev_warn - curr_warn),
    }


def fmt_list(values, limit=8):
    values = list(values)
    if not values:
        return 'none'
    if len(values) <= limit:
        return ', '.join(values)
    return ', '.join(values[:limit]) + f' (+{len(values)-limit} more)'


def main():
    skip_extraction = os.environ.get('MITCHELL_SKIP_EXTRACTION') == '1'
    run_dir = None
    if not skip_extraction:
        live = run(LIVE_CMD, cwd=AUDIT_REPO)
        if live.returncode != 0:
            print('Mitchell weekly refresh failed during live extraction.')
            stderr = (live.stderr or live.stdout or '').strip()
            if stderr:
                print(stderr[-3500:])
            sys.exit(1)
        live_out = (live.stdout or '').strip().splitlines()
        run_dir = Path(live_out[-1].strip()) if live_out else None
    build = run(BUILD_CMD, cwd=DASH_REPO)
    if build.returncode != 0:
        print('Mitchell weekly refresh failed during dashboard rebuild.')
        print((build.stderr or build.stdout or '').strip()[-3500:])
        sys.exit(1)
    publish = run(PUBLISH_CMD)
    if publish.returncode != 0:
        print('Mitchell weekly refresh failed during dashboard publish.')
        print((publish.stderr or publish.stdout or '').strip()[-3500:])
        sys.exit(1)

    dashboard_path = DASH_REPO / 'data' / 'dashboard-data.json'
    data = json.loads(dashboard_path.read_text())
    if run_dir is None:
        run_name = data.get('run_name')
        run_dir = AUDIT_REPO / 'output' / run_name if run_name else None
    if not run_dir or not run_dir.exists():
        print('Mitchell weekly refresh could not determine current run directory.')
        sys.exit(1)

    STATE_DIR.mkdir(parents=True, exist_ok=True)
    prev = json.loads(STATE_PATH.read_text()) if STATE_PATH.exists() else None
    curr = build_snapshot(run_dir, dashboard_path)
    diff = diff_snapshot(prev, curr)
    STATE_PATH.write_text(json.dumps(curr, indent=2) + '\n')

    summary = curr.get('summary', {})
    avail = curr.get('available_summary', {})
    warning_counts = curr.get('warning_type_counts', {})
    top_warning_bits = ', '.join(f"{k}: {v}" for k, v in sorted(warning_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:4]) or 'none'

    print('Mitchell weekly extraction completed.')
    print(f"Review dashboard: {URL}")
    print(f"Run: {curr.get('run_name')} — {curr.get('data_source_note')}")
    print('')
    print('Current totals:')
    print(f"- Listings scanned: {summary.get('total listings scanned', '?')}")
    print(f"- Part rows extracted: {summary.get('total part rows extracted', '?')}")
    print(f"- Overlapping parts: {summary.get('overlapping parts', '?')}")
    print(f"- Price mismatches: {summary.get('price mismatches', '?')}")
    print(f"- Warning rows: {summary.get('warnings', '?')}")
    print(f"- Unique available parts: {avail.get('unique_parts', '?')}")
    print('')
    if diff['first_run']:
        print('Review status: baseline established; no prior extraction available for delta comparison yet.')
        print('Discrepancy delta vs previous extraction: no prior baseline yet.')
    else:
        new_discrepancies = (
            len(diff.get('new_overlap_parts', []))
            + len(diff.get('new_price_mismatch_parts', []))
            + int(diff.get('new_warning_count', 0))
        )
        if new_discrepancies > 0:
            print(f'Review recommended: {new_discrepancies} new discrepancy signals detected since the last extraction.')
        else:
            print('No new discrepancies since the last extraction.')
        print('Discrepancy delta vs previous extraction:')
        print(f"- New overlap parts: {len(diff.get('new_overlap_parts', []))} ({fmt_list(diff.get('new_overlap_parts', []))})")
        print(f"- Resolved overlap parts: {len(diff.get('resolved_overlap_parts', []))} ({fmt_list(diff.get('resolved_overlap_parts', []))})")
        print(f"- New price mismatch parts: {len(diff.get('new_price_mismatch_parts', []))} ({fmt_list(diff.get('new_price_mismatch_parts', []))})")
        print(f"- Resolved price mismatch parts: {len(diff.get('resolved_price_mismatch_parts', []))} ({fmt_list(diff.get('resolved_price_mismatch_parts', []))})")
        print(f"- New warning signatures: {diff.get('new_warning_count', 0)}")
        print(f"- Resolved warning signatures: {diff.get('resolved_warning_count', 0)}")
    print('')
    print(f"Top warning types: {top_warning_bits}")
    print('Bookmark URL stays stable across refreshes: ' + URL)

if __name__ == '__main__':
    main()
