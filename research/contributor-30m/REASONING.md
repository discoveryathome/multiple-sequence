# Exact row-profile coordinate optimization

The original method uses a linear gap surrogate to propose profile changes,
then rejects them under the real affine objective. The trial investigates
whether faithfully modeling the objective can help more than repeated proposals.

Hold every row except one fixed. Remove columns that are empty in the fixed
profile. All pair scores among fixed rows are invariant to inserting columns
of gaps, so their contribution is a constant. Only pairs involving the moving
row must be optimized.

At each dynamic-programming cell (consumed moving residues i, consumed profile
columns j), track two bit masks: I for pairs currently in a gap in the profile
row, D for pairs currently in a gap in the moving row. Neither bit means the
last pair column was a residue match. The masks are disjoint. A pair's previous
state skips double-gap columns, exactly as the project model requires.

For a match step, the moving residue meets the next profile column: score all
residue/residue pairs and charge open or extend for profile gaps. New state is
(the column's gap mask,0). An insertion aligns a moving residue to gaps in all
profile rows; it sets (all,0). A deletion puts a gap in the moving row and
consumes the profile column: residue bits become D, while profile-gap bits
retain their earlier state. Cost depends only on the masks and current step.

Therefore histories at the same (i,j,I,D) have identical possible future costs;
retain the maximum integer value. Induction over the acyclic grid proves the
computed optimum for this FIXED PROFILE, subject to the state budget. Traceback
constructs a feasible alignment whose full SP is rechecked. This is not an
optimum over all multiple alignments: cycling rows is coordinate ascent and may
stop at a local optimum. The state count can grow sharply; an exceeded limit
raises an explicit failure instead of returning an approximate result labeled
exact. Budget is two million created states per row.

The implementation was checked against exhaustive insertion/deletion/match
paths for tiny gapped profiles, including cases where double gaps preserve a
gap run. Native integer bit counting is used when available, with a Python 3.9
fallback added after the initial selected-case run began. That run used the
preserved `row_dp_v1.py`; subsequent runs use `row_dp.py`. The difference is
only the popcount implementation. Both hashes and outputs are retained.

This is a new contribution to THIS pilot. Single-row iterative refinement and
affine dynamic programming are established techniques; no algorithmic novelty
or literature priority is asserted.

## Reachable-state bound

The bit masks do not imply that all 3^n theoretical vectors must be visited.
At a cell (i,j) with i>0, consider the last transition consuming a moving-row
residue. It was either M at some profile column k in 1..j, or I after some
column k in 0..j. Every subsequent transition was D, and its mask updates are
determined entirely by profile columns k+1..j. Thus there are at most 2j+1
possible histories of this form and no more distinct mask states. With i=0,
only the all-deletion path is possible. The grid therefore has O(m*L^2)
reachable states in the worst case (m=sequence length, L=profile length), with
bit operations also depending on mask word length n. Actual states often merge
much more aggressively. The memory limit is still important for long proteins.
