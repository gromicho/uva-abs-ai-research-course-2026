# Optional: auditing a machine-checked proof

Instructor demo for Lab 4 (theory part), about 10 minutes. Follows Marc's suggestion to look at AI together with Lean.

## The point

"Lean accepted the proof" and "the claim is proved" are different statements. A proof assistant checks that the conclusion follows from the stated definitions and assumptions. It does not check that the definitions mean what the title says, or that the assumptions are harmless.

## Small examples (`labs/lean-audit-demo/`)

Needs only Lean 4 and its standard library.

- `RejectedProofDemo.lean` tries to prove `2 + 2 = 5` with `rfl`. Lean rejects it.
- `LeanAuditDemo.lean` gets a "conclusion" accepted by assuming the hard step as an axiom. `#print axioms` exposes it. The honest version takes the hard step as an explicit hypothesis and gives only a conditional result.

Expected `#print axioms` output:

```
'TeachingExample.acceptedConclusion' depends on axioms: [EfficientMembership, NamedConclusion, assumedAlgorithm, reduction]
'TeachingExample.honestConditional' depends on axioms: [EfficientMembership, NamedConclusion, reduction]
```

## A real case

T. S. Arthanari, *Lean 4 Machine-Verified Proof of P = NP via the Pedigree Polytope Membership Problem* (arXiv 2606.03194; repository TiruArt/Pedigree-Polytopes-Lean4, inspected at commit `3c9c90e`, 8–9 October 2026).

- The main theorem builds with the specified toolchain (Lean 4.30.0, 2,969 build jobs, no errors). Opening question: what does a successful build establish?
- `#print axioms` on the final theorem lists ten substantive assumptions. One, `tardos_strongly_polynomial`, directly grants the efficient membership procedure, which is the central algorithmic claim. Its statement asks for no concrete algorithm, correctness proof or size bound.
- `P_equals_NP` is an opaque proposition with no formal link to complexity classes, and the polytope type is `Unit`.
- A conditional version that takes the membership procedure as an explicit input also compiles, and its axiom list no longer contains `tardos_strongly_polynomial`. That isolates the missing obligation. It is not a repaired proof.

This shows a gap in the formalisation. It is not a counterexample to the informal argument.

## Possible participant task

Generate a list of proof obligations with a reasoning assistant (Yenan's approach), then use Lean to inspect definitions and assumptions. Optionally let a Lean-producing assistant attempt one narrowly stated missing lemma, with new axioms forbidden.
