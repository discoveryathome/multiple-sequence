> This assessment describes the initial frozen portfolio. The later
> [contributor rehearsal](../research/contributor-30m/REPORT.md) changes the
> practical search frontier and gives the current featured-pilot recommendation.

# Initial pilot assessment

This report covers the initial fixed-budget implementation, before any subsequent
contributor trial. Eight protein families and three substantial baseline settings
were tested. All results are local and author-checked, not independently reviewed.

## Main result

The score-selected combined search improves the objective on **3 of 8** families.
Among those, core-pair accuracy improves on **0**, declines on **1**, and stays
unchanged on **2**. Across all configurations, the best exact-score records improve
on **4 of 8** families; one gap-only result also improves reference accuracy.
These are different comparisons: the predeclared combined method is the primary
analysis, while the record table selects by score from the whole tested portfolio.
Neither selection uses reference accuracy.

| Case | n | Max length | Best baseline | Baseline SP | Combined SP | Best tested SP | Baseline core recall | Combined recall | Record recall |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| BB11001 | 4 | 91 | mafft-linsi | 188 | 188 | 188 | 0.991228 | 0.991228 | 0.991228 |
| BB11015 | 4 | 327 | famsa2 | 47 | 55 | 70 | 0.878788 | 0.878788 | 0.883838 |
| BB12021 | 6 | 85 | mafft-ginsi | 1053 | 1053 | 1053 | 1.000000 | 1.000000 | 1.000000 |
| BB20029 | 29 | 167 | mafft-linsi | 25595 | 25691 | 25865 | 0.864192 | 0.864107 | 0.864192 |
| BB20030 | 47 | 155 | mafft-ginsi | 258594 | 258628 | 258628 | 0.902550 | 0.902550 | 0.902550 |
| BB30027 | 20 | 172 | mafft-linsi | 3479 | 3479 | 3498 | 0.893062 | 0.893062 | 0.893062 |
| BB40010 | 9 | 214 | mafft-ginsi | 1897 | 1897 | 1897 | 0.857013 | 0.857013 | 0.857013 |
| BB50013 | 18 | 318 | mafft-ginsi | 60185 | 60185 | 60185 | 0.948639 | 0.948639 | 0.948639 |

The primary BB20029 loss is one reference pair out of 11,774, despite a +96
model-score gain. The best portfolio BB11015 gap-only result gains six pairs
out of 1,188 (+0.505 percentage points) alongside +23 model-score units. That
single small-family result is encouraging but does not establish a general
method or evolutionary discovery. Exact numerator/denominator evidence is in
`results/evaluation.json`.

The highest-SP baseline is not always the most accurate baseline: four cases
have a different baseline with better core-pair recall. For example, BB20030
MAFFT L-INS-i has lower SP than G-INS-i but higher reference recall. Therefore
"we beat the baseline" must say which quantity and which baseline it means.

## Association analysis

One combined candidate per family is selected by score only. Normalize the SP
delta by the number of row pairs, then compare it with the within-family
accuracy delta. This avoids pooling raw scores across different family sizes.
There are eight family units, not 24 independent seed replicates. Pearson r is
-0.0315; Spearman rho is -0.4725.
Most deltas are zero; one accuracy loss drives much of this tiny-sample pattern.
These statistics do not establish an association in either direction, and no
significance claim is made. The five exploratory evaluation cases and three
development cases are all shown; the split is not proven homolog-disjoint.

## Search evidence and saturation

| Operation-only control | Families with score gain | Accepted moves across cases |
| --- | ---: | ---: |
| block | 0 / 8 | 0 |
| subgroup | 1 / 8 | 1 |
| gap | 4 / 8 | 14 |
| profile | 1 / 8 | 1 |

Each control uses 12 proposals, as does each combined seed; gap proposals each
contain up to 16 internal trials. Thus this is an operation ablation, not an
equal-CPU performance comparison. The current profile DP solves a linear
surrogate, which may be an important reason for rejected proposals. A more
faithful affine-aware proposal is a plausible intelligence-driven contribution.

Longer continuation (seed 101, 12 rounds) on three sizes:

| Case | Start SP | Continued SP | Extra gain |
| --- | ---: | ---: | ---: |
| BB11001 | 188 | 188 | 0 |
| BB20029 | 25691 | 25804 | 113 |
| BB50013 | 60185 | 60185 | 0 |

The 56 main experiments used 104.4 aggregate recorded
wall seconds; the three continuations used 61.8 seconds.
These are observations on a shared host, not controlled speed measurements.
The baseline methods each produced identical canonical output hashes in two
single-thread runs. All 83 saved candidate/baseline alignments are rechecked;
91 comparisons including eight reference self-tests agree with the original
BAliBASE SP evaluator to its printed precision. The legacy evaluator required
an AddressSanitizer build on this host; its unmodified non-sanitizer builds
trapped, which remains a portability caveat.

## Sustained discovery potential

Assessment: **worth a bounded research pilot; not yet evidence for a flagship
biological-discovery claim**. The exact model is cheap to verify and cases split
naturally among donors. Small score gains are reachable from serious baselines,
but four of eight cases do not improve under this portfolio, and two of three
longer continuations are flat. Repeating seeds alone may exhaust the easy gains.

Agent reasoning can contribute better proposal objectives, exact incremental
scoring, boundary handling, subgroup choice, and benchmark design. The task
becomes scientifically more valuable if these changes preserve or improve
independent accuracy consistently across a broader evaluation set. The hard
part is not producing a prettier integer score; it is understanding when that
score follows the reference and when it misleads.

Suggested next gate: a timed fresh-contributor trial, then a predeclared expansion
to independent families and a second benchmark collection. Track the share of
contributors producing verified gains, time to first gain, score and accuracy
changes separately, and time spent reasoning versus running a fixed solver.
Before sustained public donations, Douglas Colkitt should set review capacity,
acceptance rules, and a reproducible independent test bank. Publication and hub
listing were not performed. No universal optimum, DNA biological result, or
new state-of-the-art alignment method is claimed.
