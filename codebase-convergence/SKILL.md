---
name: codebase-convergence
description: Audit and safely converge code, architecture, tests, configuration, and Markdown documentation when a repository has bugs, contradictions, duplication, stale guidance, unclear ownership, or accumulating technical debt. Use for evidence-backed review and targeted repair; do not use for ordinary feature development or an unrequested redesign.
---

# Codebase Convergence

Make a repository internally consistent and easier to change. Judge four qualities with evidence: correctness, consistency, completeness, and cleanliness. Never claim that a repository is fully correct; state what was verified and what remains uncertain.

## Non-negotiable constraints

- Read repository instructions, the domain glossary, relevant ADRs, and authoritative specifications before judging implementation.
- Preserve unrelated worktree changes. Touch only files that trace to the request and remove only orphans created by this work.
- Treat user-designated text, titles, data definitions, and other protected content as locked and preserve it verbatim.
- Treat scanner, reviewer, and specialist output as candidates until their locations, claims, and impact are grounded in the current repository state.
- Do not silently change a number, business rule, state transition, public interface, interaction behavior, visual contract, or canonical owner. Put unresolved choices in one decision packet.
- Prefer the smallest contract-preserving repair: restore the behavior already established by the Interface and authoritative evidence without redefining either. Do not add an abstraction, option, Seam, fallback, or broad error handling without demonstrated need.
- Verify the finding and its proposed remedy separately. Only a finding with a current evidence basis may authorize repair or support a completion claim.
- Keep one canonical owner for each fact. Replace repeated specifications with links rather than new summaries.
- Do not infer permission to commit, push, deploy, publish, delete, or contact external systems from permission to review or repair.

## Start contract

Before multi-step work, state:

1. requested scope and excluded areas;
2. assumptions and protected content;
3. whether the user requested audit-only, direct repair, or both;
4. coverage strategy and success checks that can actually be run.

If the request is clear, proceed after stating the contract. Ask only when a missing answer would change the result materially or authorize a risky action.

Use this compact shape when helpful:

```text
Scope:
Excluded / protected:
Mode:
Verification:
```

## Load only the guidance needed

- Always read [Execution workflow](references/execution-workflow.md).
- Read [Documentation convergence](references/documentation-convergence.md) when Markdown, configuration, schemas, contracts, or code-to-doc consistency are in scope.
- Read [Architecture deepening](references/architecture-deepening.md) only when architectural friction is requested, a local fix is blocked by ownership, or evidence supports a deeper module.
- Read [Specialist routing](references/specialist-routing.md) only when a specialist Skill could materially improve a finding. Do not load specialists by default.

For a broad repository inventory, use the bundled read-only collector when available:

```bash
python3 <skill-directory>/scripts/collect_evidence.py --root <repository> --pretty
```

Treat its JSON as an inventory and evidence-basis seed, not as proof of correctness or canonical ownership. Its worktree fingerprint identifies observed Git-visible content; it is not an immutable snapshot. Inspect relevant files and run repository checks before recording a finding.

## Operating modes

- **Audit only**: inspect and report; do not edit, commit, or perform external writes.
- **Safe convergence**: apply direct repairs when the user asked to fix or converge. Finish independent safe work before sending a decision packet; after asking, pause for the user's answer.
- **Architecture exploration**: report candidates before changing an Interface, Seam, ownership, or behavior, unless the user already authorized the exact refactor.

When the user's wording is ambiguous, default to audit only for external or destructive actions and to the smallest reversible local action for repository work.

## Result contract

Return one concise, evidence-backed handoff containing:

- scope and coverage manifest, including inspected and uninspected surfaces;
- baseline, including pre-existing failures or unrelated changes;
- findings by ID, severity, confidence, evidence, impact, canonical owner, and disposition;
- direct repairs mapped to finding IDs;
- the single decision packet, if any;
- verification commands with before and after outcomes;
- unresolved risks and unverified surfaces.

Do not dump raw specialist output or imply certainty beyond the checks performed.
