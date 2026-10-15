# Polling and run-level inventory

Much of the gap to Apple is chips being polled and CPUs not reaching deep idle, not heavy code. Rates are
interrupts per second, measured on the 14" M1 Pro with `powerlab/sample.py` (battery discharging, 21%
brightness, apps open) unless noted. Rates vary with activity; treat them as orders of magnitude until the A/B
tests below are done.

| Source | Rate | What it is | Next test |
| --- | --- | --- | --- |
| `b01f00000.nhi` rx/tx rings (USB4 host) | ~1,290 each, only with the Dell WD22TB4 dock attached on kernel `7.1.13-elementary-fairydust-usb4-dptunnel` | The kernel retries a DisplayPort tunnel every ~76 ms: `thunderbolt-apple-nhi: 0:5 <-> 1:14 (DP): DPRX read timeout`, 1,684 times by 722 s uptime and still going. Started when the dock came up (~594 s). Same family as the `dock-dp-retry-silent` verify check | A/B docked vs undocked at the same brightness. Kernel-side fix: back off or stop after N DPRX timeouts. Owner's kernel: propose, do not change |
| `38bc08000.mbox-recv` (display coprocessor) | ~480 | Display controller mailbox. NOT explained by compositor flips: tracing `drm_vblank_event_queued/delivered` for 4 s at idle (2026-10-15) recorded 0 events, so Gala is not presenting frames then (assuming the driver emits those tracepoints) | Look at DCP firmware housekeeping, backlight/ambient traffic, and the mode refresh rate (120 Hz offered); Gala's 11 to 18% CPU is separate and unexplained |
| `406408000.mbox-recv` | ~385 | Another coprocessor mailbox (suspected audio/sensor) | Stop each client in turn |
| `39b10c000.spi` (keyboard/trackpad HID) | 228 to 1000 | Rises while touching | Compare hands-off vs touching |
| `arch_timer` | ~3,000 to 4,700 total (about 300 to 470 per CPU) | Timer ticks | Check tickless idle, timer slack |
| `IPI1 call interrupts` | ~1,800 to 3,900 | Cross-CPU function calls | Identify the caller (cpufreq, RCU, timers) |
| `brcmf_pcie_intr` (Wi-Fi) | ~60 | Wi-Fi chip | Check power-save scheduling |
| `mseries-keyboard-backlight` | 1 read / 5 s | Ambient-light polling for the keyboard light | Lengthen or event-drive |
| `netusage` logger | periodic | Sampling and SQLite writes | Batch writes |

## Run levels

- cpuidle exposes only `WFI` and `CPU PD`; `CPU PD` was entered about 1.8% as often as `WFI`
  (18,197 vs 1,009,020 entries on CPU 0), so deep idle is rare. Find what keeps wakeups frequent.
- Governor `schedutil` on all three clusters; profile `balanced` on AC, `power-saver` on battery
  (CPUs capped at 2064/2208 MHz by `mseries-power`).
- Runtime PM: the dock hub, the tether device, and two PCIe functions show `control=on`.
- Wi-Fi power save is on. PCIe ASPM policy is `default`.

## Method for each row

Alternate off/on three times with `powerlab`, compare medians, log in `RESULTS.md`.

## Kernel work items at idle (tracefs `workqueue:workqueue_execute_start`, 4 s, 2026-10-15)

Screen on, apps open (including the Claude desktop app being used), Dell dock attached, kernel `...-usb4-dptunnel`.
Total **41,560 work items (about 10,400/s)**; tracing itself adds some. By function:

| Function | Items | Per s | Owner |
| --- | --- | --- | --- |
| `ring_work` | 10,067 | 2,500 | Thunderbolt/USB4 NHI rings (the DP retry loop) |
| Asahi `workqueue::SubmittedWorkContainer` | 9,134 | 2,300 | Asahi GPU driver (Rust): GPU job submission |
| `drm_sched_run_job_work` | 7,132 | 1,800 | DRM scheduler: running GPU jobs |
| `tb_cfg_request_work` | 5,044 | 1,260 | Thunderbolt config requests (DP retry loop) |
| `apple_rtkit_rx_work` | 3,347 | 840 | Apple coprocessor (RTKit) mailbox receive |
| `drm_sched_free_job_work` | 2,599 | 650 | DRM scheduler: freeing GPU jobs |
| `wq_barrier_func`, `usb_giveback_urb_bh`, `commit_work`, `kcryptd_crypt`, btrfs | under 1,200 each | | misc |

Grouped: **GPU job scheduling about 18,800 (45%)**, **USB4/Thunderbolt about 15,100 (36%)**, coprocessor mailbox ~3,300 (8%).
Scheduler wakeups by task over 5 s: 67,862 total; top kworkers, then `claude-desktop` 5,265, `VizCompositorTh` 2,357 and
`Compositor` 2,016 (Chromium/Electron GPU compositing), `gala` 1,795, `gh` 1,758, `mi-scavenger` 1,574.

Reading: at "idle" the GPU is being handed about 1,800 jobs a second, almost certainly by Chromium/Electron apps
compositing at 120 Hz plus Gala; this lines up with the 2 W saved by halving the refresh rate. The dock retry loop
is the other third of kernel activity. Both are targets: (1) A/B with Electron apps closed or with GPU
compositing/background throttling flags, and with 60 Hz; (2) docked vs undocked. Running kernel is also built with
`CONFIG_HZ=1000` (and `NO_HZ_FULL`); 250 Hz is the usual laptop choice; a kernel decision for the owner.
Caveat: the measurement session itself drives the Claude app, which inflates the app and GPU lines.

## Who feeds the GPU at idle (tracepoint `gpu_scheduler:drm_sched_job_queue`, 4 s, 2026-10-15)

2,662 jobs queued (about 665/s), counted by the submitting process:
`claude-desktop` 1,461 (55%), `io.elementary.terminal` 720 (27%; it hosts an OpenCode TUI session, itself 13% CPU),
`gala` 481 (18%). The agent interfaces we use to work are the largest source of idle GPU traffic. Per-process GPU
counters (`drm-*` in fdinfo) are not exposed by this driver, so the tracepoint is the way to attribute. The measuring
session itself drives the Claude app, so this is an upper bound for a quiet desktop. A fair lean-profile number needs
those UIs closed: run `powerlab/lean-test.sh --yes` yourself (owner-triggered; it opens one fullscreen video).
