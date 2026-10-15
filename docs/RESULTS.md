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
