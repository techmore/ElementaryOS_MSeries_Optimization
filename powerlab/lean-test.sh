#!/usr/bin/env bash
# Owner-run "lean profile" measurement: idle, then local H.264 video through the hardware decoder.
#
#   bash powerlab/lean-test.sh --yes [--idle 180] [--video 300] [--clip FILE]
#
# It changes NOTHING on screen and closes nothing. It only measures and, for the video phase, opens ONE fullscreen
# muted mpv window that it closes afterwards. Before running: unplug the charger, close the agent UIs (Claude desktop,
# the Terminal running OpenCode, Brave) or accept that they count, and set brightness/refresh the way you want the
# result to represent (the script records the current values). Run it from a text console or SSH to avoid load.
# Output: powerlab/results/*.json and a summary with battery hours = energy_full / median watts.
set -euo pipefail
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
idle=180 video=300 clip="" yes=0
while [[ $# -gt 0 ]]; do case $1 in
  --yes) yes=1;; --idle) shift; idle=$1;; --video) shift; video=$1;; --clip) shift; clip=$1;;
  -h|--help) sed -n '2,12p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0;;
  *) echo "unknown option: $1" >&2; exit 2;; esac; shift; done
[[ $yes -eq 1 ]] || { echo "Refusing to run without --yes (it opens a fullscreen video for $video s)."; exit 2; }
bl=/sys/class/backlight/apple-panel-bl
echo "brightness $(cat $bl/brightness)/$(cat $bl/max_brightness); AC online=$(cat /sys/class/power_supply/macsmc-ac/online); kernel $(uname -r)"
[[ $(cat /sys/class/power_supply/macsmc-ac/online) == 0 ]] || echo "WARNING: charger connected; battery readings may not reflect total draw."
python3 "$here/sample.py" --seconds "$idle" --label lean-idle --save | head -1
if [[ -z $clip ]]; then
  clip=$(mktemp --suffix=.mp4)
  ffmpeg -v error -y -f lavfi -i "testsrc2=size=1920x1080:rate=30:duration=60" -pix_fmt yuv420p -c:v libx264 -preset veryfast -crf 23 -g 60 "$clip"
fi
mpv --fs --mute=yes --loop-file=inf --really-quiet --hwdec=vaapi "$clip" >/dev/null 2>&1 & mpid=$!
trap 'kill $mpid 2>/dev/null || true' EXIT
sleep 20
python3 "$here/sample.py" --seconds "$video" --label lean-video-hw-1080p30 --save | head -1
kill $mpid 2>/dev/null || true
full=$(cat /sys/class/power_supply/macsmc-battery/energy_full)
echo "energy_full=$((full/1000)) mWh. Hours = energy_full / median watts (video: Apple claims 17 h on 70 Wh, about 4.1 W)."
