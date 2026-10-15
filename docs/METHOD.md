# Measurement method

1. Unplug the charger. Fix brightness and Wi-Fi. Close what the scenario does not need.
2. `python3 powerlab/sample.py --seconds 60 --label <scenario> --save`. It samples
   `/sys/class/power_supply/macsmc-battery/power_now` once a second and reports the **median** and the 10th/90th
   percentile (single readings spike above 20 W when commands run), plus the busiest interrupt lines.
3. Run from a console or over SSH where possible so measuring does not add load.
4. Change one thing. Alternate off/on/off/on/off/on and compare medians. Only a gap larger than the spread
   between identical runs counts.
5. Log the result in `RESULTS.md` with date, kernel, commit and scenario.

Scenarios: idle screen off; idle at 20% brightness; local 1080p video in Brave; scripted browsing; CPU burst;
local-AI prompt.
