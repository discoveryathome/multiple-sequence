# Exact model: MSA-SP-v1

Given fixed, nonempty sequences s₁,…,sₙ, n ≥ 2, a feasible alignment is a
rectangular array over residues and `-` such that deleting gaps in row i yields
exactly sᵢ. IDs must be unique and identical to the input ID set; row ordering is
irrelevant. All-gap columns are forbidden. Residues are indexed from 1 within
their original ungapped sequence. FASTA case is normalized to uppercase.

For each unordered row pair i<j, delete every column containing two gaps. For
this projected pair, let Rᵢⱼ be its residue/residue columns and Gᵢⱼ its maximal
runs of gaps in one row opposite residues in the other. Adjacent runs on
opposite sides are different runs. A double-gap column cannot interrupt a run.

S(A) = Σᵢ<ⱼ [ Σ_(x,y)∈Rᵢⱼ B(x,y) − Σ_g∈Gᵢⱼ (o + (|g|−1)e) ].

Maximize S(A). Terminal gaps have the SAME cost as internal gaps. Weights are
uniform: each unordered pair appears once. No guide-tree, sequence weighting,
structural terms, end-gap exemptions, or biological reference terms enter S.
Every arithmetic operation affecting acceptance is an integer operation. Strict
improvement is required; ties retain the current alignment.

Protein: B is the complete integer BLOSUM62 table in `data/matrices/BLOSUM62`,
with open o=11 and extension e=1. The B/Z/X entries are explicit table entries;
U/O/J/stop symbols and arbitrary ambiguity transformations are rejected.
DNA: alphabet A/C/G/T only, match +2, mismatch −1, o=5, e=1. The library and
unit tests support this model; the biological experiments in this pilot are
PROTEIN ONLY. RNA, ambiguous DNA, codons and DNA reference benchmarking remain
outside the evaluated scope. CLI benchmark cases use the protein model.

Neither the chosen parameters nor an SP optimum are claimed to represent true
evolution. MAFFT and FAMSA have their own scoring systems; we score all their
outputs under this one declared external model. A higher external score does
not imply that we improved their native objective or their biological accuracy.

`msa.core.score` implements a pair-state scan. `oracle_score` independently
projects pairs and explicitly counts runs. Tests exercise hand-computed values,
all paths for short binary DNA sequences, invalid alignments and surrogate DP
optimality on tiny cases. `python -m msa check` always validates before scoring.
Internal scoring functions also accept partial windows, so they deliberately
are not substitutes for the public validator.

## Accuracy is a different quantity

For the supplied BAliBASE XML core mask, define P_ref as the set of
(sequence-ID, residue-index, sequence-ID, residue-index) pairs co-aligned in
reference core columns. Let P_test include aligned residue pairs from ALL test
columns. Core pair recall = |P_ref ∩ P_test| / |P_ref|. We store the numerator
and denominator as integers. This accuracy fraction is sometimes called SP
accuracy or SPS in the literature; it is never the integer optimization score.

Core pair precision uses only candidate pairs whose two residues belong to
reference core positions; ambiguous regions outside the core are not called
errors. Strict core-column recall counts an exact match of the complete
residue-index-or-gap vector in a reference core column anywhere in the
candidate. Gap positions, sequence IDs and residue indices matter. These
metrics are invariant to row order and candidate column offsets.

The original BAliBASE 3.01 evaluator assumes all n residues occupy each core
column when it forms its pair denominator. The external cross-check asserts
that assumption on our cases. Its legacy TC is truncated to integer percent;
we retain that diagnostic, while reporting our exact integer TC counts.

No accuracy term is imported by `msa/refine.py`. During the recorded generation
run, macOS sandbox rules denied reads of both `data/references` and `data/source`.
The entire reference is evaluated only AFTER candidates have been saved.

## Refinement operations and their limits

- Block: rank 40-column windows by model score, draw from the four weakest,
  strip window gaps and progressively realign in a seeded order. Splice into
  the full alignment and rescore; boundary gap runs are thus charged correctly.
- Subgroup: partition by agreement to a seeded anchor row and realign the two
  resulting profiles after deleting subgroup-only empty columns.
- Gap relocation: sample up to 16 run/side moves; shift a complete gap run across
  one neighboring residue and select the best exact-score move.
- Profile: remove one seeded row and optimize its placement against the rest.

Profile DP exactly optimizes a LINEAR cross-profile surrogate with residue-gap
cost 4, existing gap-gap cost 0, and the declared substitution matrix. It
preserves each group's internal columns. It is a proposal mechanism, NOT an
exact optimizer for pair-projected affine SP. Traceback ties prefer diagonal,
then left, then right. All four operations face the same full affine-score
acceptance check. Rejected moves are recorded, not silently omitted.

The DP costs O(L₁L₂) storage for traceback and O(L₁L₂ times profile alphabet
support) time; the authoritative scorer costs O(n²L). The implementation favors
clarity over scale. No global-optimum or polynomial-time solution is claimed.
