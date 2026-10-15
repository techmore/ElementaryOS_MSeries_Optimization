# DRAFT (not sent): `asahi-audio-no-suspend.conf` costs about 1.2 W on battery

Intended for `omacom/omarchy-mac-pkgs` (file `omarchy-mac/share/wireplumber/wireplumber.conf.d/asahi-audio-no-suspend.conf`,
audited at 222f7a8). Review before anyone posts it; posting is outward-facing and needs the owner's go-ahead.

**What happens.** The rule sets `session.suspend-timeout-seconds = 0` on the AppleJ speaker and headphone sinks so the
amplifiers never power down between streams (avoids a pop on each start and stop). With nothing playing, the speaker
ALSA stream stayed in state RUNNING.

**Measurement** (MacBookPro18,3 / M1 Pro, elementary OS 9 on Pantheon, battery, 105/500 brightness, CPU ~87% idle,
same machine, same session): 12.9 W with the rule, 11.7 W after a 30 s timeout closed the stream (about -1.2 W, 9%).
Means of 6 samples each, before we moved to median-based runs; treat as indicative.

**Suggested options:** a 30 s timeout instead of 0; or 0 only while on AC power; or document the battery cost.
Trade-off: a pop after more than 30 s of silence.

Evidence and method: `docs/RESULTS.md`, `powerlab/sample.py` in `techmore/ElementaryOS_MSeries_Optimization`.
