# Tuning drop-ins

Configuration files that change behaviour without patching code. Each ships install, uninstall and
`--dry-run`. Current:

- `wireplumber/50-mseries-asahi-no-suspend.conf`: idle sink suspend timeout 30 s instead of never
  (copy to `~/.config/wireplumber/wireplumber.conf.d/` or `/etc/wireplumber/wireplumber.conf.d/`, then
  `systemctl --user restart wireplumber`). Measured about -1.2 W; see `docs/RESULTS.md`.
- `refresh-rate/`: `mseries-refresh` switches the built-in panel to 60 Hz on battery and 120 Hz on AC (about -2 W
  at 21% brightness). Install with `bash tuning/refresh-rate/install.sh [--dry-run] [--enable]`; uninstall with
  `--uninstall`. Not enabled by default. Test: `python3 tuning/refresh-rate/test_refresh.py`.
