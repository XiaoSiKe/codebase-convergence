# Specialist routing

The Skill is the coordinator and evidence ledger owner. Use a specialist only when it can materially improve an in-scope finding and the specialist is available in the current environment.

## Routing table

| Trigger | Specialist | Expected contribution |
| --- | --- | --- |
| Hard-to-reproduce bug, crash, or performance regression | `diagnose` | Reproduction, minimized case, hypothesis, instrumentation, regression evidence |
| User explicitly requests test-first work | `tdd` | Red-green-refactor loop through the affected Interface |
| Unfamiliar subsystem or unclear relationship to the whole | `zoom-out` | Domain and dependency context before local edits |
| Evidence supports a deeper Module or a leaking Seam | `improve-codebase-architecture` | Candidate analysis using Depth, Leverage, and Locality |
| Frontend UX, accessibility, responsive behavior, or visual consistency is in scope | `impeccable` | Focused interface audit or repair without changing product intent |
| Skill packaging itself is the target | `skill-creator` | Progressive disclosure, metadata, package structure, and validation |
| Coding or refactoring risks overcomplication | `karpathy-guidelines` | Explicit assumptions, surgical scope, simpler implementation, verifiable goals |

Use a language-, framework-, security-, database-, document-, or deployment-specific Skill when it is available and the finding genuinely requires that expertise. Availability does not imply permission to perform external writes.

## Coordination rules

1. Load the minimum specialist set; do not fan out by technology name alone.
2. Give the specialist a bounded finding or exploration question, relevant repository instructions, and the raw evidence needed. Do not prime it with a desired conclusion.
3. Keep specialists read-only unless the user authorized repair and file ownership is unambiguous.
4. Translate useful results into the main evidence ledger with stable finding IDs. Do not return multiple disconnected reports.
5. A specialist recommendation cannot bypass the decision packet, locked content, repository instructions, or authorization limits.
6. If a specialist is unavailable, continue with the core workflow when safe and disclose the reduced verification surface.
