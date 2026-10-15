# Working agreement (Codex, Claude Code, OpenCode)

- Read the main repo's `mseries/OS9-HANDOFF.md` and `mseries/ROADMAP.md` before starting. Record concrete
  changes, commands, measurements, blockers and the next task in `docs/RESULTS.md` here and in the main handoff.
- One agent performs Git writes at a time. A delegated worker reports to its coordinator instead of committing.
- Never describe a configuration check as a measured improvement. A change counts only with before/after
  medians from `powerlab`.
- Do not change the owner's bootloader, kernel, initramfs or the speaker-safety daemon (`speakersafetyd`)
  without their go-ahead. Do not remove the 80% charge limit.
- Efficiency changes must be reversible: ship an uninstall and a `--dry-run`.
- Keep upstream licenses and attribution; do not import sponsor-only or SSPL code.
