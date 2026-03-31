# AGENTS.md — System Boundaries

This file defines system-layer boundaries for autonomous agent operation.

---

## 1. Context Priority

When sources conflict, use:

1. live system state
2. local control plane state (`control/*.json`, systemd status, logs)
3. ops/*.md
4. repository code/config
5. memory files
6. README / narrative docs

Reality beats documentation.
Control plane beats stale narrative.

---

## 2. Heartbeat Boundary

**Heartbeat is a platform-level wake/visibility mechanism, not the project control brain.**

It may:
- surface state
- trigger bounded low-risk checks
- help expose unread events or summaries

It must NOT replace:
- phase policy
- queue semantics
- acceptance policy
- project-specific execution boundaries

**Platform heartbeat ≠ project timer.**

| Layer | Component | Purpose |
|-------|-----------|---------|
| OpenClaw heartbeat | `~/.openclaw/openclaw.json` | Agent session wake/sleep, platform visibility |
| Project timer | `systemd openclaw-agent*.timer` | Control-plane task execution scheduling |

They are independent layers. One does not substitute the other.

---

## 3. Acceptance Semantics

Do not conflate:
- task outcome (success/failed)
with
- source truth level (L1-L4)

For read-only audit / verification work:
- report the task outcome separately
- do not imply that source truth changed just because the repo is clean and synced

For source-changing work:
- do not claim completed unless the relevant source-truth requirements are satisfied.

---

## 4. Runtime Override Rule

Temporary runtime overrides do not automatically become static truth.

Examples:
- test timer enabled for validation
- temporary scheduling or manual-trigger mode
- one-off local verification runs

If a runtime override should become long-term truth:
- re-audit it
- update the correct static source
- document the change

---

## 5. Status Bridge Rule

`control/status.md` is a consumer-facing bridge, not a loose narrative note.

Requirements:
- derive it from one coherent snapshot
- avoid mixing stale queue counts with fresh runtime facts
- if snapshot consistency is uncertain, prefer fixing the bridge over adding more fields

---

## 6. Principle

Reality first.
Analysis before escalation.
Action by default.
Documentation always.
