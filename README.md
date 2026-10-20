# Multiple sequence alignment optimization — Discovery@Home local pilot

Can intelligent refinement improve an exact alignment objective when it starts
from strong modern alignments, and do those improvements help biological
reference accuracy? This pilot measures the two questions separately.

The local package contains an integer affine sum-of-pairs validator/scorer,
eight original BAliBASE families (4–47 sequences; six categories), reproduced
MAFFT L-INS-i/G-INS-i and FAMSA2 baselines, four refinement operations, 56 main
experiments, three longer continuations, and an independent BAliBASE evaluator
cross-check. The fixed protein model is BLOSUM62 with gap open 11, extension 1,
and penalized terminal gaps. DNA has exact toy tests, but no biological dataset
in this initial release.

```sh
python3 scripts/verify.py
python3 scripts/replay.py
```

Python 3.9+; standard library only for saved-result verification and refinement.
The offline check takes seconds on the pilot host; replay takes a few minutes.
See [reproduction instructions](docs/REPRODUCE.md) for external method builds,
source hashes, per-case checks and candidate commands.

**Contributor rehearsal:** a subsequent 30-minute trial developed an exact affine
row optimizer. It improved SP on 11/12 full cases, but reference pair recall
fell on eight. See the [featured-pilot assessment](research/contributor-30m/REPORT.md)
and candidate artifacts before choosing new work. These are pending review;
the initial table below remains the frozen original experiment.

Initial result: combined refinement gains score on 3/8 families, with no core
accuracy gain and one slight loss. Selecting the best score across all tested
strategies improves 4/8 families, including one small reference-accuracy gain.
This is an optimization result with mixed biological consequences, not proof of
biological superiority. Read the [assessment](docs/ASSESSMENT.md),
[exact model](docs/MODEL.md), and [literature audit](docs/LITERATURE.md).

There is no universal best alignment absent a model and dataset. The external
frontier includes [MAFFT's consistency-based refinement](https://mafft.ddbj.nig.ac.jp/alignment/software/algorithms/)
and [FAMSA2](https://doi.org/10.1038/s41587-026-03095-3); our
[record table](discover/records.json) reports only the best locally tested value
for each pinned case. Global optimality and a new state-of-the-art method are
not claimed.

Start contributing at [AGENTS.md](AGENTS.md) and [DISCOVERY.md](DISCOVERY.md).
Douglas Colkitt is the consenting maintainer; results await his review and review
capacity is unspecified. This is LOCAL mode: nothing has been published, pushed,
posted or submitted to a hub. Code is MIT; third-party data retain their own
terms. Verifier/frontier changes deserve the most care, and review capacity will
set the pace of sustained donations.
