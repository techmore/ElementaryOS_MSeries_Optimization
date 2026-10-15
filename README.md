# ElementaryOS_MSeries_Optimization

Power lab, efficiency patches and Rust ports for **elementary OS on Apple Silicon** (MacBook Pro 14", M1 Pro).
Companion to [techmore/ElementaryOS_MSeries](https://github.com/techmore/ElementaryOS_MSeries), which holds the
image build, installers and hardware bring-up. This repo holds the measured, optional work to make the machine
**run minimal and scale fast**.

## Goal

Idle and light use close to Apple's published battery figures, with full CPU/GPU speed within seconds when
local AI or a build needs it. Targets, method and suspects: [`docs/EFFICIENCY-GOALS.md`](docs/EFFICIENCY-GOALS.md).
Today: about 11.7 W on battery in light use, roughly 2x to 3x Apple's light-use figure. We have not beaten
Apple; this repo exists to close that gap with numbers, not claims.

## Layout

| Path | What |
| --- | --- |
| `powerlab/` | Measurement harness: 1 Hz battery-power sampler, median/p10/p90 report, top interrupt rates; `results/` holds one JSON per run |
| `patches/` | One folder per efficiency patch: the patch, what it does, measured watts before and after, how to apply and undo |
| `tuning/` | Configuration drop-ins (WirePlumber, udev, systemd, sysctl) with install, uninstall and `--dry-run` |
| `rust/` | Cargo workspace for the Rust ports (`mseries-power` first; scaffold currently lives in the main repo's `deb/mseries-plugin-repo` branch and moves here with history) |
| `docs/` | Goals, method, results |

## Rules

- Measure with medians over at least 30 s, alternate on/off at least three times, one change at a time.
- Record every result in `docs/RESULTS.md` and `powerlab/results/`.
- Do not change the owner's bootloader, kernel, initramfs or the speaker-safety daemon without their go-ahead;
  test such changes in a VM or edge lane first. See [`AGENTS.md`](AGENTS.md).
- Keep licenses and attribution for anything derived from upstream (patches to elementary components are GPL-3.0).

## Quick start

```bash
python3 powerlab/sample.py --seconds 60 --label idle-20pct --save   # on battery, charger unplugged
python3 -m unittest powerlab.test_sample
```
