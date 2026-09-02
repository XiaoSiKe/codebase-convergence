# Architecture deepening

Read this reference only when architecture is requested, a local repair is blocked by unclear ownership, or the evidence ledger shows recurring friction across callers.

## Vocabulary

- **Module**: a unit with one Interface and an Implementation.
- **Interface**: everything callers must know, including types, invariants, ordering, configuration, performance expectations, and error modes.
- **Implementation**: behavior hidden inside a Module.
- **Depth**: Leverage provided through the Interface. A deep Module hides substantial behavior behind a small Interface; a shallow Module exposes nearly as much complexity as it contains.
- **Seam**: the place where behavior can vary without editing callers.
- **Adapter**: an Implementation satisfying an Interface at a Seam.
- **Leverage**: capability callers gain per unit of Interface they must learn.
- **Locality**: change, bugs, knowledge, and verification concentrated in one Module.

Use these terms consistently in architectural findings.

## Explore before proposing

Read the project's domain vocabulary and ADRs, then trace real call paths. Look for evidence that understanding or changing one concept requires bouncing between shallow Modules, that state or rules leak across a Seam, or that tests must bypass the public Interface.

Apply the deletion test: imagine deleting the suspected Module. If complexity disappears, it is likely pass-through. If the same complexity spreads into multiple callers, the Module is earning its keep. Do not introduce a Seam for one Adapter; one Adapter is a hypothetical variation, while two demonstrate a real one.

Treat package manifests, exports, documented imports, external call sites, and accepted compatibility records as evidence of a public Interface. When that evidence is absent, distinguish “one caller inside this repository” from “no external callers”; do not claim the latter without proof.

## Admit quality candidates narrowly

Use these lenses only to explain evidence already in scope; they are not a mandatory whole-repository scan:

- Contract strength: show a reachable illegal state, a declaration that conflicts with runtime behavior, or a real boundary-validation gap.
- Responsibility: identify at least two independent change reasons and the resulting test, ownership, deployment, or coordination cost. Size alone is not evidence.
- Failure integrity: trace what the caller or operator observes and show false success, hidden failure, corrupted state, unbounded recovery, or material loss of diagnostic context.
- Knowledge duplication: prove that copies encode the same rule, mapping, schema, invariant, or policy and are expected to change together. Similar syntax across independent domains is not duplication.

Do not recommend a stronger contract, split, error mechanism, or shared abstraction unless it reduces the demonstrated cost without adding greater indirection or fragility.

## Separate candidates from repairs

A candidate that changes an Interface, Seam, ownership, business behavior, or public contract is not a direct repair. Present it before implementation unless the user already authorized that exact refactor.

For each candidate, include:

- files and affected Modules;
- evidence-backed friction;
- plain-language direction without designing the Interface prematurely;
- expected Locality and Leverage;
- effect on the test surface;
- ADR conflict, if reopening it is justified;
- recommendation strength: strong, worth exploring, or speculative.

When three or more relationships are difficult to compare in prose, write a self-contained before/after HTML report to the OS temporary directory. Keep generated review artifacts out of the repository, and provide a Markdown fallback when browser or network rendering is unavailable.

## After selection

Define the chosen Module's Interface, invariants, error modes, ownership, and surviving tests with the user. Keep internal Seams private unless multiple Adapters justify exposing them. Verify behavior before and after; a refactor is not complete if callers must learn more or if complexity merely moves sideways.
