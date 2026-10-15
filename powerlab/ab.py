#!/usr/bin/env python3
"""Paired fast-alternation A/B: many short OFF/ON pairs back to back, so slow drift cancels.

  python3 powerlab/ab.py --on 'systemctl --user stop foo' --off 'systemctl --user start foo' --rounds 10 --window 12

Each round measures the lever OFF (baseline) then ON; the report is the median of the per-round differences (ON - OFF),
the spread of those differences, and how many rounds went each way. Calls --off at the end whatever happens.
A result counts only if the median difference is larger than the spread and the signs agree in most rounds.
"""
import argparse
import statistics
import subprocess
import sys
import time

sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__))))
from powerlab import sample  # noqa: E402


def measure(seconds):
    system = sample.find_system_power()
    values = []
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        time.sleep(1)
        values.append(sample.read_watts(system))
    return statistics.median(values)


def paired(rounds, window, on, off, settle=2, measure_fn=measure, run=lambda c: subprocess.run(c, shell=True)):
    diffs, offs, ons = [], [], []
    try:
        for _ in range(rounds):
            run(off); time.sleep(settle); base = measure_fn(window)
            run(on); time.sleep(settle); lever = measure_fn(window)
            offs.append(base); ons.append(lever); diffs.append(lever - base)
    finally:
        run(off)
    ordered = sorted(diffs)
    spread = ordered[len(ordered) * 3 // 4] - ordered[len(ordered) // 4] if len(ordered) >= 4 else max(diffs) - min(diffs)
    return {'rounds': len(diffs), 'median_diff_w': round(statistics.median(diffs), 2), 'iqr_w': round(spread, 2),
            'lower': sum(d < 0 for d in diffs), 'higher': sum(d > 0 for d in diffs),
            'median_off_w': round(statistics.median(offs), 2), 'median_on_w': round(statistics.median(ons), 2)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--on', required=True); ap.add_argument('--off', required=True)
    ap.add_argument('--rounds', type=int, default=10); ap.add_argument('--window', type=int, default=12)
    ap.add_argument('--label', default='lever')
    a = ap.parse_args()
    r = paired(a.rounds, a.window, a.on, a.off)
    verdict = 'REAL' if abs(r['median_diff_w']) > r['iqr_w'] and max(r['lower'], r['higher']) >= 0.8 * r['rounds'] else 'NOT DISTINGUISHABLE FROM NOISE'
    print('%s: ON-OFF median %+.2f W (iqr %.2f; ON lower in %d/%d rounds); OFF %.2f W, ON %.2f W -> %s' % (
        a.label, r['median_diff_w'], r['iqr_w'], r['lower'], r['rounds'], r['median_off_w'], r['median_on_w'], verdict))


if __name__ == '__main__':
    main()
