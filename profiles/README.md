# Profiles

`mseries-profile` applies only levers measured in `docs/RESULTS.md`, as named profiles. Dry run by default; `--apply` to act;
`--display` adds the one visible lever (refresh rate). It never touches brightness, the kernel, the bootloader,
`speakersafetyd` or the charge limit, and needs no root.

| Profile | What it does | Measured effect |
| --- | --- | --- |
| `battery` | idle speaker sink suspends after 30 s; power profile `power-saver`; with `--display` 60 Hz | about -1.2 W (audio, low confidence), about -2 W (60 Hz); `power-saver` alone measured -0.10 W (noise) |
| `balanced` | undoes the above | back to defaults |
| `burst -- CMD` | switches to `balanced` while CMD runs, then restores the previous profile (a hold is impossible here) | see the gap below |

**Gap found 2026-10-15:** power-profiles-daemon here offers only `balanced` and `power-saver`: `performance` is "not available" and only `performance` or `power-saver` can be held, and `mseries-power` caps the CPUs directly on battery, which a held profile does not lift. Making the cap
follow the active profile (a natural job for the planned Rust port of `mseries-power`) is what would give a real "ramp up when
needed" on battery. The CPU itself ramps in about 78 ms once the cap allows it.

This is a tool, not a result: with every lever applied the machine is still far from Apple's 4.1 W (video) and 6.4 W (web).
