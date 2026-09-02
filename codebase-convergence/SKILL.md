---
name: codebase-convergence
description: Frequently fix bugs, review code, and safely simplify or converge a scoped area or whole repository when code, tests, configuration, schemas, migrations, generated artifacts, or documentation may be incorrect, contradictory, duplicated, stale, or hard to maintain. Use during active maintenance, after changes, or before release; do not use for ordinary feature creation or speculative redesign.
---

# Codebase Convergence

Improve a repository's correctness, internal consistency, simplicity, and ease of change. Use the Skill repeatedly for focused bug repair, code review, active cleanup, or broader project convergence. Scale coverage to the request; a local bug does not authorize an unrelated whole-repository rewrite.

## Two inseparable core disciplines

Apply both disciplines on every run. They are built into this Skill, not optional specialist routes.

1. **Precise execution**: surface assumptions, prefer the simplest complete solution, change only evidence-backed scope, remove only resulting or explicitly requested residue, and define checks that prove the requested outcome. Minimum means the smallest change that resolves the demonstrated problem, not the fewest edited lines.
2. **Deep-Module convergence**: inspect in-scope code through Module, Interface, Implementation, Depth, Seam, Adapter, Leverage, and Locality. Concentrate rules, bugs, knowledge, and verification behind a small Interface without moving complexity sideways.

The architecture lens is always active, but it does not manufacture refactors. Use the detailed architecture tests only on in-scope evidence and propose or implement deepening only when real caller, change, ownership, or test friction supports it.

## Non-negotiable constraints

- Read repository instructions, the domain glossary, relevant ADRs, and authoritative specifications before judging implementation.
- For a bug, first build the fastest reliable feedback loop that reproduces or otherwise proves the reported failure. If the exact symptom cannot be established, report the verification gap instead of fixing a nearby guess.
- Preserve unrelated worktree changes. Every changed line must trace to the request and a current Finding; do not stage, revert, format, or clean unrelated work.
- Treat scanner, reviewer, and specialist output as candidates until their locations, claims, impact, and evidence basis are grounded in the current repository state.
- Do not silently change a number, business rule, state transition, public Interface, interaction behavior, visual contract, canonical owner, or accepted ADR. Put unresolved choices in one decision packet.
- Prefer the simplest complete, contract-preserving repair. Do not add an option, fallback, abstraction, Seam, or error handling for an unobserved scenario.
- Verify the Finding and its remedy separately. A current Finding only makes a remedy eligible for review; it does not prove the remedy or grant authorization.
- Keep one canonical owner for each fact. Replace repeated specifications with stable links or callers rather than a second source of truth.
- Do not infer permission to commit, push, deploy, publish, delete, or contact external systems from permission to review or repair.

## Start contract

Before multi-step work, state:

1. requested scope and excluded or protected areas;
2. assumptions and whether the request is audit-only, repair, simplification, or architecture exploration;
3. coverage proportional to the request;
4. observable success checks that can actually be run.

If the request is clear, proceed. Ask only when a missing answer changes the result materially or authorizes risky work.

## Scope and authorization are separate

- **Focused bug repair**: reproduce the symptom, trace the affected Module, callers, tests, contracts, and canonical owner, then check the same root cause across that relevant surface.
- **Scoped review or convergence**: inspect and repair only the named area and its proven dependencies.
- **Whole-project review or convergence**: only when explicitly requested, inventory the repository breadth-first, then trace changed, central, and high-risk paths deeply. Report uninspected surfaces.
- **Audit only**: report admitted Findings and architecture candidates without repository mutation.
- **Safe convergence**: apply direct repairs, including the contract-preserving internal-deepening subtype, when requested and supported by evidence.
- **Architecture exploration**: report before changing an Interface, Seam, ownership, behavior, or ADR unless the user already authorized that exact refactor.

## Load only the detail needed

- Always read [Execution workflow](references/execution-workflow.md).
- Always apply the compact architecture lens above. Read [Architecture deepening](references/architecture-deepening.md) when code is in scope; scale its candidate reporting to the evidence.
- Read [Documentation convergence](references/documentation-convergence.md) when Markdown, configuration, schemas, generated artifacts, contracts, or code-to-doc consistency are in scope.
- Read [Specialist routing](references/specialist-routing.md) only when another Skill can materially improve an in-scope Finding.

For a broad inventory, use the bundled read-only collector when available:

```bash
python3 <skill-directory>/scripts/collect_evidence.py --root <repository> --pretty
```

For a non-trivial, externally supplied, cross-file, or cross-turn Finding, use the machine-readable [Finding contract](references/finding-contract.md) and bundled validator without writing artifacts into the target repository:

```bash
python3 <skill-directory>/scripts/finding_contract.py stamp --root <repository> --finding <draft.json>
python3 <skill-directory>/scripts/finding_contract.py check --root <repository> --finding <stamped.json>
```

The whole-worktree fingerprint records the observed scene. Per-Finding file fingerprints determine whether declared evidence is still current. Neither proves semantic correctness, complete coverage, canonical ownership, architectural quality, or permission to repair.

## Result contract

Return one evidence-backed handoff containing:

- requested scope and a coverage manifest, including uninspected surfaces;
- baseline, reproduction or verification gap, and unrelated pre-existing state;
- Findings by stable ID, severity, confidence, evidence, impact, freshness, canonical owner, and disposition;
- repairs mapped to Finding IDs, including why each remedy is the simplest complete change;
- Interface, Depth, Leverage, Locality, and test-surface effects for architecture work;
- one consolidated decision packet, if needed;
- verification commands with before and after outcomes;
- residual risks without claiming full correctness.

Do not dump raw tool or specialist output. Say what was verified and what remains uncertain.
