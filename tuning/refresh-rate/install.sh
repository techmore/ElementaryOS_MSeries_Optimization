#!/usr/bin/env bash
# Install the refresh-rate switcher for the current user.
#   bash install.sh [--dry-run] [--enable]   install (add --enable to start it now and at login)
#   bash install.sh --uninstall              remove it (and restore 120 Hz via --once is up to you)
set -euo pipefail
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
dry=0 enable=0 uninstall=0
for a in "$@"; do case $a in --dry-run) dry=1;; --enable) enable=1;; --uninstall) uninstall=1;; *) echo "unknown: $a" >&2; exit 2;; esac; done
run() { printf '  $ %s\n' "$*"; [[ $dry -eq 1 ]] || "$@"; }
bin=$HOME/.local/libexec/mseries-refresh unit=$HOME/.config/systemd/user/mseries-refresh.service
if [[ $uninstall -eq 1 ]]; then
  run systemctl --user disable --now mseries-refresh.service || true
  run rm -f "$bin" "$unit"; run systemctl --user daemon-reload; exit 0
fi
run install -Dm755 "$here/mseries-refresh" "$bin"
if [[ $dry -eq 1 ]]; then echo "  (would write $unit)"; else
  mkdir -p "$(dirname "$unit")"
  cat >"$unit" <<UNIT
[Unit]
Description=Panel refresh rate follows the power source (60 Hz on battery, 120 Hz on AC)
PartOf=graphical-session.target
After=graphical-session.target

[Service]
ExecStart=$bin
Restart=on-failure

[Install]
WantedBy=graphical-session.target
UNIT
fi
run systemctl --user daemon-reload
[[ $enable -eq 0 ]] || run systemctl --user enable --now mseries-refresh.service
echo "Installed. Not enabled unless --enable was given. Status: $bin --status"
