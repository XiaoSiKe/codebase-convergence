# Execution workflow

Use this workflow for every convergence task. Keep the Interface stable—scope, admitted Findings, decisions, repairs, and verification—while scaling the Implementation to the request.

## 1. Turn the request into observable success

1. State scope, exclusions, protected content, assumptions, authorization, and checks that would demonstrate success.
2. Choose proportionate coverage. A focused Bug repair traces the affected Module and relevant callers; a scoped review stays within named code and proven dependencies; a whole-project request inventories every major surface before deep tracing.
3. For a reported Bug, build the fastest reliable feedback loop at the Interface where the symptom occurs: a failing test, reproducible command, request, browser flow, trace replay, or other deterministic check. Confirm it matches the user's failure, not a nearby one.
4. If no reliable reproduction or decisive evidence is available, record the attempted checks and verification gap. Do not compensate with speculative fallbacks.

## 2. Establish the repository baseline

1. Inspect repository instructions and worktree state. Record unrelated changes without staging, reverting, cleaning, or formatting them. Retain the collector's Git head and worktree fingerprint when available.
2. Identify relevant entry points, Modules, callers, state and knowledge owners, tests, configuration, schemas, migrations, generated artifacts, UI flows, and documents.
3. Read domain vocabulary and accepted ADRs before judging an Interface or moving ownership. If neither exists, infer cautiously from authoritative code and documents and label the inference.
4. Discover existing formatter, lint, type-check, test, build, generator, and UI verification commands. Run a proportionate pre-edit baseline when safe and useful; record commands, exit codes, and failure summaries.
5. Identify generated artifacts and their source chain. Modify a wrong canonical source before running the existing generator; if only the artifact is stale, rerun the generator without a no-op source edit.
6. Search references, callers, data flow, error modes, and documented contracts before assuming impact or absence.

Do not install tools or build a general scanning framework solely for the review. The bundled collector seeds inventory and whole-worktree context; its heuristics are leads, not Findings.

## 3. Admit one evidence ledger

Give each Finding a stable ID and record:

- one precise claim and category: `bug`, `contradiction`, `duplication`, `stale-or-dead`, `completeness-gap`, or `architecture-candidate`;
- severity, confidence, and reachable user or maintainer impact;
- decisive evidence: file and line, test, command, or reproducible path;
- evidence basis: whole-worktree context plus files relevant to this Finding;
- freshness: `current`, `stale`, or `unknown`;
- canonical owner and any uncertainty about it;
- disposition: direct repair, decision required, architecture candidate, or observation.

Scanner, reviewer, and specialist output begins as a candidate. Confirm cited locations and contracts exist, read the complete logical block and necessary callers, and prove claimed impact is reachable. Verify a shared premise once before adjudicating dependent candidates; reject the group when that premise fails.

For a non-trivial, external, cross-file, or cross-turn Finding, materialize the machine-readable [Finding contract](finding-contract.md) outside the target repository and run `scripts/finding_contract.py`. The validator checks structure, safe paths, line ranges, and declared file freshness. It cannot establish semantic truth, complete the relevant-file set, choose the canonical owner, assess Depth or Locality, validate a remedy, or grant permission.

Only a `current` Finding is eligible for remedy review. Re-ground `unknown` external Findings. Mark a Finding `stale` when a declared subject, caller, test, contract, generated source, or canonical owner changes. An unrelated file change does not stale it; an undeclared new caller remains a limitation and must be sought again before high-risk work.

A smell without demonstrated cost is an observation. Similar syntax, file size, broad types, catch-all handling, fallbacks, or repeated lines are investigation signals only. Merge Findings only when their root claim, canonical owner, impact, and evidence basis match.

## 4. Judge each Finding through both core disciplines

### Precise execution

- State competing interpretations rather than silently choosing one.
- Prefer the simplest complete remedy that addresses the demonstrated root cause.
- Reject flexibility, compatibility layers, options, Seams, and error handling for unobserved scenarios.
- Keep every changed line traceable; do not repair adjacent observations unless the user included them in scope.
- Define the exact before/after signal before implementation.

### Deep-Module convergence

Apply the contract, Locality, deletion, Interface-test-surface, and Adapter-reality checks from [Architecture deepening](architecture-deepening.md) to the relevant code surface. The lens is mandatory; an architecture Finding is not. Record no candidate when the code already has adequate Depth or evidence is insufficient, and do not widen scope merely to find a candidate.

## 5. Classify the remedy before editing

- **Direct repair**: restores established behavior through the existing Interface without changing a business rule, public contract, interaction, number, or owner. Its contract-preserving internal-deepening subtype may concentrate proven repeated knowledge or failure handling inside an existing Module when the user requested repair or convergence and before/after Interface tests exist.
- **Decision required**: conflicting authoritative evidence leaves a material value, rule, state, behavior, or canonical owner unresolved.
- **Architecture candidate**: changes an Interface, Seam, ownership, behavior, or accepted ADR. Report it before implementation unless the exact refactor was already authorized.
- **Observation**: lacks evidence, reachable impact, or a proportionate remedy. Do not modify code for it.

Complete independent safe work before sending one consolidated decision packet. Include affected files, conflicting interpretations, evidence, impact, options, tradeoffs, and a recommendation or explicit uncertainty. Pause only when the unresolved choice blocks further work.

## 6. Implement the smallest complete change

1. Re-read the target and recompute Finding freshness immediately before editing.
2. Confirm the proposed remedy—not merely the Finding—is necessary, proportionate, and contract-preserving.
3. Change the smallest coherent Module surface that resolves the root cause. A one-line caller patch is not smaller when it preserves the same leaked rule across several callers.
4. Exercise the behavior through the Interface callers use. Turn the reproduction into a regression test at that Interface when a correct test surface exists.
5. Update the canonical owner once and make dependants call or link to it.
6. Remove only imports, code, tests, prose, and instrumentation made obsolete by this work or explicitly included in the cleanup request.

If the real defect cannot be isolated, return to evidence gathering. Do not hide uncertainty behind broader exception handling or fallback behavior.

## 7. Verify and re-adjudicate

Repeat relevant baseline checks and classify outcomes as before, after, unchanged, or not run:

- original reproduction and focused Interface regression tests;
- formatter, lint, and static analysis;
- broader tests and build when proportionate;
- generator and idempotence checks;
- UI or end-to-end checks for affected flows;
- Markdown links, examples, headings, and references to canonical facts;
- final diff for scope, unrelated formatting, accidental value or behavior changes, duplicate owners, and debug residue.

Any repair changes its Finding's evidence basis. Re-adjudicate affected Findings against the combined final state; do not label stale evidence as fixed. For architecture work, compare the before/after Interface, surviving tests, and whether Depth, Leverage, or Locality actually improved.

## 8. Hand off with calibrated certainty

Report scope and coverage, baseline, admitted Findings, repairs, decisions, verification, and residual risks. Explain why each remedy was the simplest complete change and, when architecture changed, where complexity and knowledge became more local. Say “verified by …” rather than “guaranteed.”
