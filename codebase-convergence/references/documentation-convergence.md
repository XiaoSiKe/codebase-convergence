# Documentation convergence

Read this reference when documents, configuration, schemas, public contracts, or code-to-doc consistency are in scope. Documentation convergence serves knowledge Locality: maintain each fact at one canonical owner and make dependants link to it rather than relearn it.

## Assign one responsibility per document

Respect existing conventions. If the repository has no clear model, prefer these roles:

- entry point: purpose, setup, and links;
- architecture map: modules, Interfaces, ownership, and major flows;
- domain specification: terms, rules, invariants, and canonical values;
- ADRs: durable decisions and rationale;
- runbooks: operational procedures;
- status or plans: current work only, kept short-lived.

Do not create a new document merely to repeat these sources. Durable rationale belongs in an ADR; current progress does not.

## Build a canonical-source map

For every disputed fact, identify its canonical owner and all dependants. Check at least the relevant pairs:

- domain rule ↔ implementation ↔ tests;
- configuration default or limit ↔ code ↔ deployment example ↔ documentation;
- public type, command, endpoint, error mode, or event name ↔ callers ↔ examples;
- schema ↔ migration ↔ model ↔ serialization;
- source schema or template ↔ generator ↔ generated code or documentation;
- UI state transition ↔ state owner ↔ rendered copy ↔ accessibility behavior;
- setup command or environment variable ↔ package scripts ↔ CI and runbooks.

Never assume implementation is authoritative solely because it runs. A contradiction may expose an implementation bug, a stale test, or an obsolete document.

For each relevant relationship, classify the alignment state:

- `aligned`: the sources express the same contract;
- `contradiction`: two sources require incompatible values or behavior;
- `required-but-missing`: an established authoritative requirement has no implementation;
- `public-behavior-undocumented`: public or contractual behavior exists but its expected specification owner does not cover it;
- `ambiguous`: the meaning or canonical owner cannot be established from current evidence.

Every non-aligned record names both source locations, user impact, candidate canonical owner, and disposition. Do not treat every internal implementation detail as a documentation gap, and do not promote executable behavior to canonical truth merely because it runs.

## Converge prose safely

- Merge documents only when they own the same responsibility.
- Preserve locked blocks verbatim. If moving them changes context or numerical representation, include the move in the decision packet.
- Retain a fact once at its canonical owner and replace repetitions with stable links.
- Preserve the historical identity of old PRDs, plans, and logs. Delete, rewrite, or archive them only when the user authorized that lifecycle change.
- Remove stale examples or explanations only after proving they are superseded and unreferenced.
- If the canonical source of generated documentation is wrong, modify it and run the repository's existing generator. If the source is already correct and only the artifact is stale, rerun the generator without changing the source. If the source chain is ambiguous, require a decision.
- Update inbound and outbound links after renames or moves.
- Keep examples executable or explicitly illustrative; do not let an example become a second specification.

## Markdown quality checks

Check heading order, duplicate headings, local links and anchors, code-fence balance and language tags, tables, list nesting, referenced paths and commands, and terminology from the domain glossary. Search for copied numeric values, rule wording, environment variables, command flags, and public names that may drift.

Report unresolved contradictions with both statements and their evidence. Do not smooth over disagreement with vague prose. A whole-project review must state what was inspected and what received only static or no verification.
