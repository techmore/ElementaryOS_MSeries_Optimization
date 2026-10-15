# Tuning drop-ins

Configuration files that change behaviour without patching code. Each ships install, uninstall and
`--dry-run`. Current:

- `wireplumber/50-mseries-asahi-no-suspend.conf`: idle sink suspend timeout 30 s instead of never
  (copy to `~/.config/wireplumber/wireplumber.conf.d/` or `/etc/wireplumber/wireplumber.conf.d/`, then
  `systemctl --user restart wireplumber`). Measured about -1.2 W; see `docs/RESULTS.md`.
