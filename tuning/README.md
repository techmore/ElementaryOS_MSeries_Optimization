# Tuning drop-ins

Configuration files that change behaviour without patching code. Each ships install, uninstall and
`--dry-run`. Current:

- `wireplumber/50-mseries-asahi-no-suspend.conf`: idle sink suspend timeout 30 s instead of never
  (copy to `~/.config/wireplumber/wireplumber.conf.d/` or `/etc/wireplumber/wireplumber.conf.d/`, then
  `systemctl --user restart wireplumber`). Measured about -1.2 W; see `docs/RESULTS.md`.
- `refresh-rate/`: `mseries-refresh` switches the built-in panel to 60 Hz on battery and 120 Hz on AC (about -2 W
  at 21% brightness). Install with `bash tuning/refresh-rate/install.sh [--dry-run] [--enable]`; uninstall with
  `--uninstall`. Not enabled by default. Test: `python3 tuning/refresh-rate/test_refresh.py`.
- `refresh-rate/` also has an idle-driven **dynamic mode** (`mseries-refresh --dynamic`, or `dynamic = true` in
  `~/.config/mseries/refresh.conf`): after `idle_seconds` (default 15) without input it drops to `low_hz` (60) and returns to the
  source's rate on input, never switching more often than `min_dwell_seconds` (20). It reads Mutter's `IdleMonitor`
  (`GetIdletime`, confirmed available on this desktop). Decision logic is unit-tested (8 tests pass); **the daemon loop has
  not been run on the real display**, and a mode switch blanks the screen briefly (how long is unmeasured), so try it only
  with the owner present. True variable refresh is not available on this stack (no Mutter VRR flag, no driver VRR property).
