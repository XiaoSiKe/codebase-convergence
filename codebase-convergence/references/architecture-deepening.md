# Architecture deepening

Apply this lens to every in-scope code review, repair, and convergence pass. Scale the analysis to the request: architecture is always considered, but a focused Bug does not trigger an unrelated repository redesign or mandatory report.

## Vocabulary

- **Module**: anything with one Interface and an Implementation, from a function to a package or tier-spanning slice.
- **Interface**: everything callers must know, including types, invariants, ordering, configuration, performance expectations, and error modes.
- **Implementation**: behavior hidden inside a Module.
- **Depth**: Leverage provided through an Interface. A deep Module hides substantial behavior behind a small Interface; a shallow Module exposes nearly as much complexity as it contains.
- **Seam**: the place where behavior can vary without editing in place; it is where a Module's Interface lives.
- **Adapter**: a concrete thing that satisfies an Interface at a Seam.
- **Leverage**: capability callers gain per unit of Interface they must learn.
- **Locality**: change, Bugs, knowledge, and verification concentrated in one Module.

Use these terms consistently in architecture Findings and avoid substituting ambiguous terms when the distinction matters.

## Explore from the domain and real call paths

Read the project's domain vocabulary and accepted ADRs, then trace actual callers. Look for evidence that understanding or changing one concept requires bouncing between shallow Modules, callers reproduce the same rule or failure handling, state leaks across a Seam, or tests must bypass the public Interface.

Use these tests proportionally:

- **Deletion test**: imagine deleting a suspected Module. If complexity disappears, it is likely pass-through. If the same complexity spreads into callers, the Module is earning its keep.
- **Interface test surface**: callers and tests should cross the same Seam. A test that must reach through the Interface may reveal the wrong Module shape.
- **Adapter reality**: one Adapter is a hypothetical Seam; expose a Seam only when at least two Adapters or another observed variation requires it.
- **Locality check**: identify where a rule, failure, change, and its verification must currently be edited. Similar syntax is not shared knowledge when domains and owners differ.

Treat manifests, exports, documented imports, external call sites, and accepted compatibility records as evidence of a public Interface. When that evidence is absent, distinguish “one caller inside this repository” from “no external callers”; do not claim the latter without proof.

## Admit quality Findings narrowly

- **Contract strength**: show a reachable illegal state, a declaration that conflicts with runtime behavior, or a real validation gap at the Interface.
- **Responsibility**: identify at least two independent change reasons and their test, ownership, deployment, or coordination cost. Size alone is not evidence.
- **Failure integrity**: trace what a caller or operator observes and show false success, hidden failure, corrupted state, unbounded recovery, or material loss of diagnostic context.
- **Knowledge duplication**: prove copies encode the same rule, mapping, schema, invariant, or policy and are expected to change together.
- **Shallowness**: show that callers learn or repeat nearly as much complexity as the Module hides.

Do not recommend a stronger contract, split, error mechanism, shared abstraction, or new Seam unless it reduces demonstrated cost without adding greater indirection or fragility. A clean architecture review may legitimately produce no architecture Finding.

## Separate internal deepening from interface decisions

A contract-preserving internal deepening may be a direct repair when all of these hold:

- the user requested repair, simplification, or convergence;
- repeated knowledge or failure handling is proven across real callers;
- the existing external Interface, behavior, ordering, error modes, and owner remain stable;
- tests exercise the same Interface before and after;
- the result increases Locality or Leverage without creating an unneeded Seam.

A candidate that changes an Interface, Seam, ownership, business behavior, visual contract, or accepted ADR requires a decision unless the exact refactor was already authorized. For each candidate, report:

- affected files and Modules;
- evidence-backed friction;
- direction in plain language without prematurely fixing the Interface design;
- expected Locality, Leverage, and test-surface effect;
- ADR conflict, if reopening it is justified;
- recommendation strength: strong, worth exploring, or speculative.

Use a self-contained before/after HTML report in the OS temporary directory only when the user requests a visual architecture review or three or more relationships are difficult to compare in prose. Keep generated review artifacts out of the repository.

## After selection

Define the chosen Module's Interface, invariants, error modes, ownership, and surviving tests with the user. Keep internal Seams private unless multiple Adapters justify exposing them. Verify behavior before and after; a refactor is incomplete when callers must learn more, tests bypass the Interface, or complexity merely moves sideways.
