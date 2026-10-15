#!/usr/bin/env python3
"""Sample battery power once a second and report robust statistics.

  python3 powerlab/sample.py --seconds 60 --label idle-20pct [--save]

Reports median, 10th and 90th percentile (single readings spike while commands run) and the busiest interrupt
lines. Reads POWERLAB_BATTERY (default /sys/class/power_supply/macsmc-battery) so tests can use a fake tree.
"""
import argparse
import json
import os
import platform
import statistics
import time
from pathlib import Path

BATTERY = Path(os.environ.get('POWERLAB_BATTERY', '/sys/class/power_supply/macsmc-battery'))
INTERRUPTS = Path(os.environ.get('POWERLAB_INTERRUPTS', '/proc/interrupts'))
RESULTS = Path(__file__).resolve().parent / 'results'


def read_watts():
    """Battery power in watts, positive while discharging (power_now is negative then on this driver)."""
    microwatts = int((BATTERY / 'power_now').read_text())
    return abs(microwatts) / 1e6


def interrupt_totals():
    totals = {}
    for line in INTERRUPTS.read_text().splitlines()[1:]:
        fields = line.split()
        if not fields or not fields[0].endswith(':'):
            continue
        count = 0
        for field in fields[1:]:
            if not field.isdigit():
                break
            count += int(field)
        totals[fields[0][:-1] + ' ' + ' '.join(fields[-2:])] = count
    return totals


def summarize(samples):
    ordered = sorted(samples)
    n = len(ordered)
    return {
        'n': n,
        'median_w': round(statistics.median(ordered), 3),
        'p10_w': round(ordered[n // 10], 3),
        'p90_w': round(ordered[min(n - 1, n * 9 // 10)], 3),
        'mean_w': round(sum(ordered) / n, 3),
        'min_w': round(ordered[0], 3),
        'max_w': round(ordered[-1], 3),
    }


def top_rates(before, after, seconds, limit=6):
    rates = sorted(((after[k] - before.get(k, 0)) / seconds, k) for k in after)[::-1]
    return [{'irq': k, 'per_s': round(rate)} for rate, k in rates[:limit]]


def run(seconds, interval=1.0, sleep=time.sleep, clock=time.monotonic):
    status = (BATTERY / 'status').read_text().strip() if (BATTERY / 'status').exists() else 'unknown'
    before = interrupt_totals()
    start, samples = clock(), []
    while clock() - start < seconds:
        sleep(interval)
        samples.append(read_watts())
    elapsed = max(clock() - start, 1e-9)
    result = summarize(samples)
    result.update({'status': status, 'top_irqs': top_rates(before, interrupt_totals(), elapsed)})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--seconds', type=int, default=60)
    parser.add_argument('--label', default='unlabeled')
    parser.add_argument('--save', action='store_true', help='write powerlab/results/<timestamp>-<label>.json')
    args = parser.parse_args()
    result = run(args.seconds)
    result.update({'label': args.label, 'kernel': platform.release(), 'time': time.strftime('%Y-%m-%dT%H:%M:%S%z')})
    if result['status'] != 'Discharging':
        print('WARNING: battery status is %s, not Discharging; the reading is not a battery-power measurement.' % result['status'])
    print('%s: median %.2f W  p10 %.2f  p90 %.2f  (n=%d, %s)' % (
        args.label, result['median_w'], result['p10_w'], result['p90_w'], result['n'], result['status']))
    for item in result['top_irqs']:
        print('  %7d/s  %s' % (item['per_s'], item['irq']))
    if args.save:
        RESULTS.mkdir(exist_ok=True)
        path = RESULTS / ('%s-%s.json' % (time.strftime('%Y%m%d-%H%M%S'), args.label))
        path.write_text(json.dumps(result, indent=2) + '\n')
        print('saved', path)


if __name__ == '__main__':
    main()
