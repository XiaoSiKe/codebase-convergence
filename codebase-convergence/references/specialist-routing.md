# Specialist routing

When invoked directly, this Skill coordinates the convergence task and owns its evidence ledger. Under an outer task governor, it owns only the repository-convergence Finding ledger; the outer governor retains the user channel, task-level authorization, and final delivery. Use a specialist only when it can materially improve an in-scope Finding and is available in the current environment.

Precise execution and Deep-Module convergence are built-in core disciplines. They remain active even when `karpathy-guidelines` or `improve-codebase-architecture` is unavailable; do not route to either merely to obtain the core behavior. Use the external architecture Skill only when the user requests its full visual candidate report or an already selected candidate needs its extended design conversation.

## Routing table

| Trigger | Specialist | Expected contribution |
| --- | --- | --- |
| Hard-to-reproduce bug, crash, or performance regression | `diagnose` | Reproduction, minimized case, hypothesis, instrumentation, regression evidence |
| User explicitly requests test-first work | `tdd` | Red-green-refactor loop through the affected Interface |
| Unfamiliar subsystem or unclear relationship to the whole | `zoom-out` | Domain and dependency context before local edits |
| User requests the full visual architecture report or extended candidate-design loop | `improve-codebase-architecture` | Visual candidates and guided design after the core workflow grounds the architecture Finding |
| Frontend UX, accessibility, responsive behavior, or visual consistency is in scope | `impeccable` | Focused interface audit or repair without changing product intent |
| Skill packaging itself is the target | `skill-creator` | Progressive disclosure, metadata, package structure, and validation |

Use a language-, framework-, security-, database-, document-, or deployment-specific Skill when it is available and the Finding genuinely requires that expertise. Availability does not imply permission to perform external writes.

## Coordination rules

1. Load the minimum specialist set; do not fan out by technology name alone.
2. Give the specialist a bounded Finding or exploration question, relevant repository instructions, and the raw evidence needed. Do not prime it with a desired conclusion.
3. Keep specialists read-only unless the user authorized repair and file ownership is unambiguous.
4. Treat specialist results as candidates. Admit them only after grounding their locations, claims, impact, and evidence basis in the current worktree; otherwise route them to re-research.
5. Translate admitted results into the repository-convergence ledger with stable finding IDs. Do not return multiple disconnected reports.
6. A specialist recommendation cannot bypass the decision packet, locked content, repository instructions, or authorization limits.
7. If a specialist is unavailable, continue with the core workflow when safe and disclose the reduced verification surface.
