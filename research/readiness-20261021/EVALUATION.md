# Proposed future evaluation — not yet approved or executed

The existing MSA-SP-v1 objective and its historical frontier remain unchanged.
There are two distinct contribution routes:

1. **Fixed-objective engineering:** exact scoring, faster equivalent operations,
   different search neighborhoods and reproducible counterexamples. Reference
   metrics are reported separately; higher integer score alone is not a biology win.
2. **Biological-method research:** a new, versioned algorithm/scoring experiment.
   Its method may be designed using the exposed development families. Its code,
   parameters, stopping rules and comparator set must be frozen before any reserve
   reference evaluation. It cannot replace MSA-SP-v1 records under different rules.

## Proposed confirmation contract

An independent curator must approve or replace `reserved-families.json` and assess
homology using appropriate sequence/structure evidence, including relations between
reserve families. The ten cases are an author-selected proposal, not a sealed or
representative external test. Add a separately sourced benchmark if terms and
comparability permit. New categories/data do not by themselves prove independence.

Pin the method, environment, seeds, all input/reference hashes and all comparator
versions before execution. Reproduce MAFFT L-INS-i, MAFFT G-INS-i and FAMSA2 on the
same full inputs; do not treat their old per-family metrics as new-case baselines.
The proposed primary comparator is MAFFT L-INS-i, chosen before reserve outcomes.
Report all three comparisons. A curator may revise this before the freeze.

Primary diagnostic: family-macro mean difference in core-pair recall. Also report
paired per-family counts, precision, strict core-column recall, median change,
number of improved/degraded families, failures, peak memory and CPU/wall budgets.
No cherry-picked seeds or excluding failures from the denominator. Use a declared
fallback baseline for method failures in any aggregate and report failure rate
separately. Bootstrap families only if a reviewer accepts their independence; a
ten-family interval is exploratory and cannot establish broad superiority.

A reference-aware guard on the exposed families is a development diagnostic, not a
reference-blind deployed algorithm. Do not select the best method per reserve case
using its reference. Score gains paired with reference losses must remain visible.
Any meaningful biological-improvement threshold and acceptance rule require review;
no threshold is retrospectively selected in this package.

## Data terms

The pinned BAliBASE archive README describes formats and citations but supplies no
explicit redistribution license. Public hosting alone does not resolve that gap.
The original upstream site could not be retrieved during this preparation. No
rights-holder contact has occurred. Public distribution remains pending an explicit
permission record or a replacement dataset with suitable terms. Existing local
research materials retain their source attribution; no new benchmark sequences or
reference outcomes were added by this preparation.

To reproduce the input-only reserve selection from a separately obtained archive:

```sh
python3 scripts/reserve_families.py --archive /path/to/BAliBASE_R1-5.tar.gz
```

The script checks the original archive digest and reads only full-length `.tfa`
inputs. It never opens XML reference alignments or core masks.
