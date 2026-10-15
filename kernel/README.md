# Kernel and scheduler notes (reference only; the kernel feature set is DeepSeek's)

> **Ownership (2026-10-15):** DeepSeek, another agent, owns the kernel feature set (fairydust, AVD/USB4/dock-video
> patches) of `techmore/ElementaryOS_MSeries`. Claude does not build, patch or install kernels, and changes no bootloader
> or m1n1 files. Everything here is measurement and context for that owner, posted as
> [a comment on issue #46](https://github.com/techmore/ElementaryOS_MSeries/issues/46#issuecomment-6201042382).
> The patch file is an untested sketch offered as reference, not a request.

Source of truth for the running kernel: `techmore/linux-m1pro-touchid`, branch `asahi`
(running `7.1.13-elementary-fairydust-usb4-dptunnel`). Nothing here has been built or booted by this repo.

## 1. Thunderbolt DPRX poll back-off (`0001-thunderbolt-dprx-poll-backoff.patch`)

Problem: with the Dell WD22TB4 attached, `thunderbolt.dprx_timeout=-1` (wait forever; set for the dock reverse-engineering)
makes `tb_dp_dprx_work()` poll the dock every 50 ms plus a 25 ms capability read, forever
(`DPRX read timeout` every ~76 ms, ~1,290 interrupts/s on each NHI ring, ~15,100 of 41,560 kernel work items in 4 s).

Change: keep waiting forever but double the poll delay from 50 ms up to 1 s (new field `tunnel->dprx_polls`,
reset in `tb_dp_dprx_start()`), about 13x fewer wakeups once the sink stays silent.
Applies cleanly to the fork's `drivers/thunderbolt/tunnel.[ch]` (checked 2026-10-15 with `git apply --check`).
Risks: when the dock's DisplayPort sink finally answers, bring-up can be up to 1 s later than today; the 25 ms
read per poll still costs a little; not compiled or run here. Test: build the kernel package, boot it from the
spare entry, dock, and compare `DPRX read timeout` rate in `dmesg`, NHI interrupts/s and `powerlab` medians docked
at identical brightness. Keep the stock entry for recovery (`mseries/fairydust/usb4/RECOVERY.md` in the main repo).

## 2. Scheduler tick (`CONFIG_HZ`, `NO_HZ_FULL`): measure first

The running config uses `CONFIG_HZ_1000=y` and `CONFIG_NO_HZ_FULL=y` (see the main repo's `mseries/fairydust/usb4/running-config`).
Candidates: `CONFIG_HZ_250=y` and `CONFIG_NO_HZ_IDLE=y`. Expected to reduce timer interrupts (`arch_timer` ran about
3,000 to 5,000/s across 10 CPUs) but **not measured**; it needs a kernel build and A/B. Do not claim a saving until measured.

## 3. Already measured, no change needed

- CPU frequency ramp: after a cap is lifted the performance cores reach 90% of 3,036 MHz in about 78 ms (schedutil
  rate limit 75 to 84 us). Scaling up is not the problem.
- Idle governor: `teo` is **worse** than `menu` here: +0.8 W (15.41/15.70 W vs 14.96/14.61 W) and about 4x fewer deep-idle
  entries. Keep `menu`.
- CPU hotplug (`cpuN/online`) is not writable on this kernel, so "fewer cores" cannot be tested at runtime.

## Build status

Not built, and not going to be built by this repo's author: see the ownership note above. The earlier request for the dptunnel
branch/commit and `.config` is withdrawn.
