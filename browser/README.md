# Browser video: make YouTube use the hardware H.264 decoder

`h264only/` is a tiny Manifest V3 extension (written here, not downloaded) that reports VP8/VP9/AV1 as unsupported on
YouTube so it serves H.264 (avc1), which the Asahi video decoder handles. Load it unpacked in a **test profile** first:

```bash
brave-browser --user-data-dir=/tmp/brave-test --load-extension=$PWD/browser/h264only \
  --enable-features=AcceleratedVideoDecodeLinuxGL,VaapiIgnoreDriverChecks
```

Measured 2026-10-15 (SMC whole-machine power, brightness 325/500, 120 Hz, charger connected, agent UIs running, 60 s medians,
one video, Big Buck Bunny): stock 19.27 W; extension 18.52 W; extension + VA-API flags 17.72 W (about -1.5 W, -8%).
Decoder interrupts in 60 s: 3,065 / 7,216 / 7,258. Caveats: one run each; stock Brave also touched the decoder this time
(an earlier run showed none), so treat the stock-vs-extension gap as an estimate. See `docs/RESULTS.md`.
