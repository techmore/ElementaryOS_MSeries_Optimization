# Rust ports

Planned crates, in order: `mseries-power` (root helper), the DNS/network usage logger, the brightness and
keyboard-light services. The first scaffold (`rust/mseries-power` with parity tests) is on the main repo's branch
`deb/mseries-plugin-repo` and will be moved here with history (`git subtree split`) once its owner agrees.
Rules: parity tests first, side by side with the current script, aarch64 build in CI, `cargo audit`/`cargo deny`,
no `unsafe` without a written reason, power measured before and after.
