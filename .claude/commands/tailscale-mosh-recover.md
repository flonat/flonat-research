---
description: 'Use when mosh hangs / fails to connect to a headless Mac mini after
  a Tailscale update or restart, OR when a remote-access tool (RustDesk, VNC, AnyDesk)
  fails to reach its public relay from an MDM-managed client. Layers — Tailscale daemon
  health (dual-install conflict, headless GUI-app limitation, Homebrew launchd takeover),
  downstream mosh-server cleanup (stale UDP bindings to old Tailscale IP), macOS resolver
  stuck state, and Tailscale direct-IP as relay-bypass fallback. Symptoms include
  `could not get canonical name for <host>`, `failed to connect to local Tailscale
  service`, `Tailscale.CLIError error 1`, `Connection closed by UNKNOWN port 65535`,
  `Failed to connect to rs-ny.rustdesk.com:21116: Please try later`.'
---

# Shared skill adapter

Read and follow `~/.claude/shared-skills/tailscale-mosh-recover/SKILL.md`. Resolve bundled resources relative to `~/.claude/shared-skills/tailscale-mosh-recover/`.
