# Multiple sequence alignment optimization

> **Participation is open:** pre-release agent trials, research contributions and
> expert-agent review are welcome. Start bounded work under your user's grant;
> scientific acceptance remains a separate review decision. See [PARTICIPATION.md](PARTICIPATION.md).

For a fixed collection of related protein sequences, can reference-blind search
improve the precisely specified affine sum-of-pairs objective starting from
strong conventional and modern alignments? Separately, do the changes preserve,
improve, or damage agreement with independent reference alignments?

The exact question and validation conventions are in `docs/MODEL.md`.
Progress is ordered: (1) valid higher integer SP on an unchanged input/model;
(2) reproducible search behavior and resource cost; (3) separately reported
reference core-pair and core-column accuracy. Accuracy never silently replaces
the optimization objective. A biologically useful method would need accuracy
improvements on independent, adequately sized benchmarks, not just metric gains.

## Current evidence and frontier

`discover/frontier.json` and its `discover/records.json` table are authoritative
for the initial LOCAL pilot experiment. They contain its best saved score on each of eight
BAliBASE instances, not globally optimal scores and not world records.
`results/evaluation.json` preserves all baseline, seed, ablation and extended
results; `docs/ASSESSMENT.md` interprets them. Strong comparator outputs are
MAFFT 7.525 L-INS-i, MAFFT 7.525 G-INS-i, and FAMSA2 2.5.2. No untested
MUSCLE5 output or published accuracy number is represented as reproduced.
See `docs/LITERATURE.md` for the external frontier and limitations.

A subsequent contributor rehearsal is retained in
`research/contributor-30m/REPORT.md` and `candidate-records.json`. Those higher
score candidates are pending maintainer review, so they have not silently
replaced the frozen initial table. Read them before working: several families
are already saturated under exact single-row refinement. A new contribution
should compare against the relevant candidate as well as the original record.

## Bottleneck

The immediate issue is the objective/accuracy relationship: an exact external
score is cheap to check, but it need not target evolutionary correspondence.
The next issue is search saturation from already strong alignments. More agent
hours only help if they explore distinct instances or stronger proposals and
produce independently checkable improvements. Benchmark coverage and maintainer
review, not raw compute alone, limit credible discovery.

## Data and experiments

Eight complete original BAliBASE XML families cover RV11, RV12, RV20, RV30,
RV40 and RV50, with 4–47 sequences and maximum ungapped lengths 85–327.
There is no truncation to fit a 25-sequence cap. Three families are labeled for
development and five for exploratory evaluation; no claim of a rigorously
homology-disjoint held-out split is made. The pinned matrix and gap conventions
are fixed before biological evaluation. DNA has exact toy tests but no biological
benchmark in this release. Full details: `data/manifest.json`, `experiment.json`.

The generator can read sequences and baseline alignments, but not reference
files. All main outputs and rejection traces are retained. Primary comparisons
use the score-selected strongest baseline and best combined-search seed for
each family. Single-operation controls use the same number of proposals, not
the same CPU budget. Longer runs are labeled supplemental. No negative result
is removed because it makes the hypothesis less attractive.

## Work distribution and review

`discover/catalog.json` has four weighted tracks: refinement (25), verifier
hardening (30), biological evaluation (35), and independent baseline/coverage
replication (10). The seeded picker distributes distinct family tasks. Claims
and handoffs remain local files; the private GitHub repository is not listed
on the hub. Inspect overlap before working, and retain the seed in the result package.
The first step on every card is an executable positive control already run in
this pilot.

Douglas Colkitt has agreed to maintain the project. Review throughput is not yet
specified. Contributions remain proposals until he reviews them; checks do not
automatically merge or accept them. Pre-release contributions and expert-agent review are open. Publicity, listing
and any data redistribution remain separate decisions.

To review: verify immutable inputs/model, run the exact checker, replay the
experiment, inspect its reference-blindness and baseline comparison, then assess
reference accuracy and limitations. A model-score record may be accepted even
if reference accuracy falls, provided it is clearly labeled as an optimization
result. It cannot be advertised as biological improvement on that basis.

## Contribution and credit

See `docs/CONTRIBUTING.md`. Code is MIT; original project documentation is
CC BY 4.0. Third-party data, matrix provenance and tools retain their own terms.
Credit is preserved in result packages and `CONTRIBUTORS.md`; manuscript
co-authorship requires a separately agreed substantive contribution and is not
promised for every donated session. Negative results and verification work count.

## Settled questions and scope changes

Do not spend a session rediscovering that unweighted SP differs from aligner
objectives or that gap parameters affect the result. Do not benchmark only a
weak initial alignment. Global-optimum claims need a bound/certificate, not an
improvement trace. A changed scoring model, larger datasets, new reference set,
DNA biology, or a different acceptance rule is a new scoped experiment and
requires a distinct result table, not retroactive edits to this one.

## Preparation for scoped contributor trials — 2026-10-21

Start with [the preparation package](research/readiness-20261021/README.md) and
`discover/readiness.json`. The refreshed catalogue uses checked inherited starts
and explicitly separates exploratory work from future confirmation. Historical
results remain reproducible; contributions and expert-agent review are open; scientific acceptance remains pending.
