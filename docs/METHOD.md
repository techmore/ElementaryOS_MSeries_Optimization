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

## Fast paired alternation (`powerlab/ab.py`) — use this when load drifts

Long A/B windows break down when your own apps change the load: on 2026-10-15 baselines wandered between 14 and 24 W in an
hour, bigger than any single lever. `ab.py` instead alternates OFF/ON in short windows (12 s) for 10 rounds and reports the
median of the paired differences, their spread, and how many rounds went each way. A lever counts only if the median
difference exceeds the spread and at least 8 of 10 rounds agree. Examples in `docs/RESULTS.md`.
