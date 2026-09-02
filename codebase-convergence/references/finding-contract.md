# Finding contract

Use the [Finding schema](finding.schema.json) and `scripts/finding_contract.py` for non-trivial, external, cross-file, or cross-turn Findings. Keep generated Finding records in task memory or the OS temporary directory unless the user asks to persist a report.

## Interface

The Module has two commands and writes JSON only to standard output:

```bash
python3 <skill-directory>/scripts/finding_contract.py stamp --root <repository> --finding <draft.json>
python3 <skill-directory>/scripts/finding_contract.py check --root <repository> --finding <stamped.json>
```

Use `-` as the Finding path to read JSON from standard input.

- `stamp` accepts a Finding draft, validates it, fingerprints its declared relevant files, sets `freshness` to `current`, and emits the complete record.
- `check` validates a stamped Finding, recomputes only its declared file fingerprints and evidence line ranges, and reports `current`, `stale`, or `unknown`.

Exit code `0` means the stamped record is current, `1` means a check found stale or unknown evidence, and `2` means the input, path, or contract is invalid.

## Draft shape

Provide every final Finding field except `freshness`. Under `evidence_basis.files`, provide only each relevant repository-relative `path` and its `role`; `stamp` owns `method`, `state`, and `sha256`.

Every `file` evidence item must name its repository-relative `path`. Use `test`, `command`, or `reproduction` for decisive evidence that has no single file location.

```json
{
  "schema_version": 1,
  "id": "F-auth-001",
  "claim": "The suspended-user branch returns allow.",
  "category": "bug",
  "severity": "high",
  "confidence": "confirmed",
  "impact": "Suspended users can enter an authenticated flow.",
  "evidence": [
    {
      "kind": "file",
      "summary": "The branch contradicts the accepted login rule.",
      "path": "src/auth.py",
      "start_line": 12,
      "end_line": 13
    }
  ],
  "evidence_basis": {
    "files": [
      {"path": "src/auth.py", "role": "subject"},
      {"path": "docs/adr/0001-login.md", "role": "canonical-owner"},
      {"path": "tests/test_auth.py", "role": "test"}
    ]
  },
  "canonical_owner": {
    "status": "confirmed",
    "path": "docs/adr/0001-login.md"
  },
  "disposition": "direct-repair"
}
```

If a whole-worktree fingerprint is available from `collect_evidence.py`, the draft may include it as `evidence_basis.worktree_fingerprint`; `stamp` preserves it as audit context.

## Canonical ownership

- The JSON schema owns field names, required fields, primitive shapes, and allowed values.
- The Python validator owns cross-field policy, safe path handling, line checks, file observation, and freshness computation.
- The Skill workflow—not the schema or validator—owns semantic admission, canonical-owner judgment, remedy assessment, architecture judgment, and user authorization.

A `confirmed` canonical owner must name a present file carrying the `canonical-owner` role in `evidence_basis.files`. An absent expected path can still be fingerprinted for a completeness Finding, but it cannot become a confirmed owner until that source exists; use `unknown` or `disputed` with a reason instead.

`eligible_for_remedy_review: true` means only that a `direct-repair` Finding is structurally valid and its declared evidence is current. It does not prove the claim, approve the remedy, or grant permission to edit.

## Limits

- File fingerprints cannot determine whether the declared relevant-file set is complete. Search callers, contracts, and generated sources again before high-risk repair.
- A new but undeclared caller does not stale the Finding.
- Ignored files, external services, runtime state, and artifacts outside the repository require separate evidence and may force `unknown`.
- Symlink evidence and paths outside the repository are rejected.
- An absent path can be fingerprinted for a completeness Finding; creating it later makes that evidence stale.
