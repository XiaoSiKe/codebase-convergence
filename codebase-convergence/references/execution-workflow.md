# Execution workflow

Use this workflow for every convergence task. Scale the depth to the repository and the user's request.

## 1. Establish a trustworthy baseline

1. Inspect repository instructions and worktree state. Record unrelated changes without staging, reverting, or formatting them.
2. Identify the requested paths, entry points, state and data ownership, tests, configuration, schemas, migrations, UI flows, and Markdown documents. When the user asks for the whole project, inventory the repository breadth-first before tracing high-risk paths deeply.
3. Read the domain glossary and accepted ADRs before implementation. If neither exists, infer vocabulary cautiously from authoritative code and documents and label the inference.
4. Identify generated files and their source chain from headers, build scripts, schemas, code generators, or repository instructions. If the canonical source is wrong, edit it before rerunning the existing generator. If the source is already correct and only the artifact is stale, rerun the generator without a no-op source edit. Do not patch a generated artifact as if it were canonical.
5. Discover the repository's existing formatter, lint, type-check, test, build, and UI verification commands. Before editing, run a proportionate baseline and record the command, exit code, and failure summary when doing so is safe and useful.
6. Search before assuming: trace references, callers, data flow, error modes, and documented contracts.

Do not install new tools or create a broad test framework solely to perform the review.

## 2. Build one evidence ledger

Give each finding a stable ID. Record:

- category: bug, contradiction, duplication, stale/dead material, completeness gap, or architecture candidate;
- severity and user impact;
- confidence: confirmed, probable, or uncertain;
- evidence: file and line, command output, failing test, or reproducible path;
- canonical owner: where the fact or behavior should live;
- disposition: direct repair, decision required, architecture candidate, or observation.

A smell without impact or evidence is an observation, not a repair mandate. Findings from specialists must be translated into this same ledger rather than emitted as a second report.

## 3. Resolve contradictions without guessing

Use this precedence as evidence, not as an automatic truth selector:

1. explicit user instruction and locked content;
2. accepted ADRs and authoritative domain specifications;
3. verified public contracts, schemas, migrations, and tests;
4. current executable behavior;
5. secondary explanations, examples, plans, and status documents.

Tests and implementation may encode the same bug. When sources conflict, trace history and callers where useful, state the impact of each interpretation, and classify the item as decision required if intent remains ambiguous.

## 4. Ask once for material decisions

Complete discovery and independent direct repairs before sending questions. Put all unresolved material choices in one decision packet, then pause for the user's answer:

- identifier and affected files;
- current conflicting values or behaviors;
- evidence and user impact;
- available options and tradeoffs;
- recommendation, or an explicit statement that evidence is insufficient.

Material items include numbers and their representation, business rules, state transitions, public interfaces, interaction or visual behavior, canonical ownership, and locked-content status. Do not edit the affected expression while it is unresolved.

## 5. Repair through the smallest useful Interface

For each contract-preserving direct repair:

1. reproduce or otherwise prove the defect when practical;
2. choose the smallest change that restores the intended invariant;
3. test behavior through the Interface callers use;
4. update the canonical owner once and link dependants to it;
5. remove only imports, code, tests, or prose made obsolete by this change.

Avoid drive-by cleanup. If a simpler repair has the same verified outcome, use it. If the real defect cannot be isolated, return to evidence gathering rather than adding speculative fallback logic.

## 6. Verify in layers

Run the existing checks relevant to changed surfaces. Repeat the same baseline commands after editing so each result can be classified as before, after, unchanged, or not run:

- formatter and lint for syntax and style;
- type or static analysis for contracts;
- focused regression tests, then broader tests when proportionate;
- build or packaging checks;
- UI or end-to-end verification for changed user flows;
- Markdown links, headings, code fences, examples, and references to canonical facts.

Inspect the final diff for scope, accidental behavior or value changes, duplicated sources of truth, generated artifacts, and unrelated formatting. Distinguish introduced failures from pre-existing failures.

## 7. Hand off with calibrated certainty

Report a coverage manifest for code, configuration, schemas, migrations, tests, generated artifacts, and documents that were inspected or could not be inspected. Then report the baseline, evidence ledger summary, repairs, decision packet, verification matrix, and residual risks. Say “verified by …” rather than “guaranteed.” Every changed line must trace to the user's request and a finding.
