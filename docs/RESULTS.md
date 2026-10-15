# Results log

| Date | Change | Scenario | Before | After | Notes |
| --- | --- | --- | --- | --- | --- |
| 2026-10-14 | WirePlumber idle sink suspend 0 s -> 30 s (`tuning/wireplumber/`) | battery, 105/500 brightness, CPU ~87% idle | 12.9 W (mean of 6 samples) | 11.7 W (mean of 6 samples) | Speaker ALSA stream was RUNNING with nothing playing. Means of short runs, before the median method; repeat with `powerlab`. Possible pop after 30 s of silence. |
| 2026-10-14 | Keyboard-backlight service stopped | same | 13.3 W | 12.4 W | Not conclusive: baseline repeat read 14.8 W; noise exceeds the effect. Redo with medians. |
| 2026-10-14 | netusage logger stopped | same | 13.3 W | 12.3 W | Same caveat. |

## Observations (no change made)

- Display-controller mailbox `38bc08000.mbox-recv` ~480 interrupts/s at idle; `406408000.mbox-recv` ~385/s; SPI HID
  `39b10c000.spi` 228 to 1000/s depending on touch. Gala 11 to 18% CPU idle.
- Wi-Fi power save is on; schedutil governor; cpuidle exposes only WFI and CPU PD states.
- Battery: 63.7 Wh full vs 69.3 Wh design (92% health).

## 2026-10-15 baselines (kernel 7.1.13-elementary-fairydust-usb4-dptunnel, Dell dock attached, charger connected, battery above the 80% limit so it was discharging)

| Scenario | Median | p10 / p90 | Notes |
| --- | --- | --- | --- |
| Brightness 500/500 after reboot, 8 s smoke run | 19.2 W | 19.0 / 20.4 | Not comparable; screen at full brightness |
| Brightness 105/500, apps open, 60 s (`baseline-20pct-apps-open`) | 13.6 W | 12.7 / 16.2 | Includes the DP tunnel retry loop (see `POLLING.md`) |

Not yet measured: the same scenario undocked, which would isolate the DP retry loop's cost.

## Negative results

- 2026-10-15: no DRM vblank events queued or delivered in 4 s at idle (screen on, apps open), so the display mailbox rate (~480/s) is not driven by compositor page flips. Do not chase compositor repaints for that line; test DCP housekeeping and refresh rate instead.

## 2026-10-15 refresh rate: 120 Hz vs 60 Hz (alternating A/B, `powerlab`, 30 to 40 s medians, battery discharging, docked, charger connected)

| Brightness | 120 Hz | 60 Hz | Difference |
| --- | --- | --- | --- |
| 500/500 (it had been reset to full) | 18.59 W, 19.11 W | 17.35 W, 17.15 W | about -1.7 W (-9%) |
| 105/500 (21%) | 13.35 W, 12.86 W | 11.43 W, 10.86 W | about -2.0 W (-15%) |

Order was 120, 60, 120, 60 each time; the difference exceeds the spread between repeats (about 0.3 to 0.5 W at the median).
Caveats: the 21% runs had p90 spikes (29.7 W once) from other activity; apps were open; only one machine. The
display mode switch does not reset brightness (checked: stayed 105), but something reset it to 500 between 14:27 and
14:38 and also after the reboot: open question.
Tool: `tuning/refresh-rate/` (opt-in; 60 Hz on battery, 120 Hz on AC, configurable, `--status`, `--once`).

## 2026-10-15 lever tests (60 Hz base, battery discharging, docked; medians of 30 s runs)

Method note: these tests changed the owner's screen and upset them; no further display tests without asking.
The baseline itself drifted 9.6 to 11.0 W between runs, so only repeated, alternated pairs count.

| Lever | Result | Verdict |
| --- | --- | --- |
| 60 Hz vs 120 Hz (earlier) | -2.0 W at 21%, -1.7 W at full brightness | Real, repeated |
| Brightness 21% -> 11% -> 5% | 9.63/9.60 W -> 9.05/9.10 W -> 8.89 W | Real but small: about -0.7 W from 21% to 5% |
| 48 Hz vs 60 Hz | 10.07 W vs neighbouring bases 11.03 and 10.49 W | Inconclusive (maybe -0.4 to -1 W); needs a clean repeat |
| Bluetooth off | 10.19 W vs bases 10.98 and 9.72 W | Inconclusive |
| CPUs 4-9 offline | not possible: writes to `cpuN/online` are denied on this kernel | No data |
| Display off (DPMS), 30 s | median 9.72 W but p10 6.27 W, p90 15.5 W | Too noisy; suggests non-display floor near 6 W with apps running |
| Keyboard backlight | already 0 in daylight | Spent |

Other: the first 11% reading (16.8 W) and a later 14.3 W/14.6 W reading were transient spikes, not effects.
Current best realistic profile with everything above: about 9 to 10 W in light use at 60 Hz and low brightness,
versus Apple's implied 4.1 W (video) and 6.4 W (web). **Not at parity.**

## Next, without touching the screen

- Dynamic refresh: the screen mode switch blanks briefly; true variable refresh (Mutter `variable-refresh-rate`
  experimental feature, DCP support unverified) would ramp without a modeset. Investigate read-only first, then ask.
- Reduce GPU job submission (about 1,800/s at idle) from Chromium/Electron apps (flags, fewer open apps).
- Kernel: `CONFIG_HZ` 1000 -> 250; back off the DP tunnel retries; deep idle (CPU PD) entry rate.
- Video playback test (YouTube 1080p in Brave with VA-API) to be run only with the owner's agreement, since it uses the screen.

## 2026-10-15 video playback (display settings left as the owner had them: 120 Hz, brightness varied)

Battery 64.3 Wh full (`energy_full`). Hours = 64.3 / watts. Apple's published figure for video is 17 h on 70 Wh (about 4.1 W).

| Test | Brightness | Median | p10 / p90 | Hardware decoder used | Hours on a full battery |
| --- | --- | --- | --- | --- | --- |
| YouTube, stock Brave, fresh profile (auto quality, VP9/AV1 expected) | 500/500 | 18.84 W | 16.6 / 20.7 | no (AVD interrupts 0) | about 3.4 h |
| Local 1080p30 H.264 in mpv, `--hwdec=vaapi`, fullscreen, muted | 325/500 | 13.23 W | 13.1 / 13.6 | yes (5,402 AVD interrupts in 90 s) | about 4.9 h |
| Same file, `--hwdec=no` (software) | 325/500 | 18.53 W | 13.3 / 28.6 | no | about 3.5 h |

Findings: the Asahi hardware decoder works from mpv and saves about **5.3 W** against software decode of the same clip.
Stock Brave on YouTube does not use it (YouTube serves VP9/AV1, which this decoder does not handle), so web video costs
about as much as software decode. Not comparable with Apple's number: brightness and refresh rate were not matched
(Apple's test uses moderate brightness; ours ran at 65% and 100%, at 120 Hz). The synthetic test clip is higher-bitrate
than typical video, which makes both decode numbers pessimistic. Rough estimate only (not measured): at 60 Hz (about -2 W)
and moderate brightness the hardware-decode case might reach about 8 to 9 W, roughly 7 to 8 h: about half of Apple's 17 h.
**Not at parity.**

## Levers identified for video, in order of expected size

1. Hardware decode in the browser: make YouTube serve H.264 (extension/user-agent policy) or add VP9 decode in the kernel driver; then confirm AVD interrupts during playback.
2. 60 Hz (about -2 W) and moderate brightness.
3. Remove the idle GPU job traffic and dock retry loop (about 80% of kernel work items at idle).
4. Kernel tick 1000 Hz -> 250 Hz; deeper CPU idle.

## 2026-10-15 scheduler and idle (no display changes)

| Test | Result |
| --- | --- |
| Idle governor `menu` vs `teo`, alternated twice, 40 s medians | menu 14.96 / 14.61 W; teo 15.41 / 15.70 W: **teo +0.8 W**, deep-idle (CPU PD) entries 19,877 / 14,557 (menu) vs 4,789 / 2,732 (teo). Keep menu |
| CPU frequency ramp from a lowered state | P-cluster reached 90% of 3,036 MHz in 76 to 79 ms; fast enough |
| Kernel work items at idle | 41,560 in 4 s: GPU scheduling 45%, USB4 DP retry loop 36% (see `POLLING.md`) |
| `thunderbolt.dprx_timeout` | `-1` on this machine (wait forever, deliberate for the dock work), polled every 76 ms |

Proposed fix for the retry cost: `kernel/0001-thunderbolt-dprx-poll-backoff.patch` (unbuilt, unmeasured).
