# Featured-pilot assessment after a contributor rehearsal

**Recommendation: keep this as a secondary optimization/methodology pilot; do not lead with a claim of better biological alignments.** There is substantial, accessible hill-climbing from strong starting points, and agent reasoning produced a useful new search operation. The fixed mathematical objective frequently rewards changes that reduce reference accuracy. A public feature could honestly demonstrate that tension, but a flagship biological discovery story needs a stronger validation result.

This was a real, bounded local contributor rehearsal starting at 2026-10-20 20:14:51 UTC. The exact duration, ending commit and environment are in `session.json`. It used a fresh checkout of `85b8c509647df7fa7b538559dd23b4b0d7fb1a49`, with seed `589bdc016c5273ab83ad9e82c6229c86` selecting `refine-bb20029`. The same agent that assembled the pilot performed the rehearsal: this is not an independent novice usability test. All candidates await Douglas Colkitt's review; no result was published or submitted to a hub.

## What a contributor accomplished

The initial pilot already had MAFFT 7.525 L-INS-i/G-INS-i, FAMSA2 2.5.2, and block, subgroup, gap-relocation and profile refinements. The contributor noticed that the profile optimizer proposed moves with a linear-gap surrogate while acceptance used the exact affine objective. It implemented a dynamic program that optimizes one complete sequence against the other fixed rows under the actual pair-projected affine score.

The program tracks gap history separately for every sequence pair, including the subtle rule that double gaps preserve previous gap state. Histories with the same grid position and gap-state masks can be merged. This reasoning changes which alignments can be found; it is more than running existing seeds longer. The optimum is exact only for that fixed profile, within the explicit state budget. Repeated row updates can get stuck at coordinate optima. `REASONING.md` gives the recurrence, justification, reachable-state bound and limitations. No literature novelty is claimed.

The first saved improvement on the selected family was +378 points approximately 2 minutes 40 seconds after the rehearsal started. Two sweeps then raised the incumbent from 25,865 to 28,470 (+2,605). Continuing the old search for approximately the same measured wall time raised it to 26,298 (+433). The new and control arms took 210.03 and 210.89 seconds respectively, in sequence on a shared host. This is useful evidence for the new move, not a controlled hardware speed benchmark or a claim that the reasoning method is six times faster.

The selected case's reference pair recall fell from 86.42% to 84.25% (255 fewer of 11,774 reference pairs). A better numerical score was therefore not better reference correspondence.

## Biological results and strong comparators

Twelve complete family experiments cover 4–47 protein sequences, with maximum sequence lengths 85–370, across six BAliBASE categories. Eight are the original pilot families; four additional families were selected by size/category before their accuracy was evaluated. The additional set is exploratory, not a preregistered representative or proven homology-disjoint test bank. A separate 91-sequence case is a three-row scaling probe, not a full sweep and not included in the twelve-case summary.

Of the twelve complete cases, 11 improved mathematical score; reference core-pair recall improved in 3, declined in 8, and stayed unchanged in 1. Two of twelve beat the best reference-pair recall among all three reproduced conventional/modern baseline outputs. This comparison is evaluated after search; references never choose a proposal. The optimizer starts from the strongest score after prior refinement, not the baseline with the best reference accuracy.

| Case | Sequences | Initial SP | Row-DP SP | Reference recall change (percentage points) | Recall change versus best of three baselines (points) |
|---|---:|---:|---:|---:|---:|
| BB11001 | 4 | 188 | 218 | -3.509 | -4.386 |
| BB11015 | 4 | 70 | 149 | -6.734 | -6.229 |
| BB12021 | 6 | 1,053 | 1,053 | 0.000 | 0.000 |
| BB20029 | 29 | 25,865 | 28,470 | -2.166 | -2.166 |
| BB20030 | 47 | 258,628 | 261,151 | -2.087 | -5.857 |
| BB30027 | 20 | 3,498 | 3,719 | -1.029 | -1.483 |
| BB40010 | 9 | 1,897 | 1,982 | -1.093 | -3.188 |
| BB50013 | 18 | 60,185 | 61,063 | -0.046 | -0.046 |
| BB11029 | 4 | -279 | -237 | +19.935 | +11.438 |
| BB12040 | 5 | 802 | 826 | -2.292 | -2.292 |
| BB30017 | 15 | -5,638 | -4,131 | +0.454 | -0.181 |
| BB50007 | 23 | -26,440 | -20,416 | +3.187 | +2.284 |

Counts and all pair precision/complete-column recall values are in `evaluation.json`; baseline-by-baseline comparison is in `biology-comparison.json`. BB30017's small pair-recall gain accompanies worse precision and column recall; it is not uniformly more accurate. The largest positive example, BB11029, still recovers only 60.13% of annotated reference pairs after its first sweep. It is an illustrative success, not evidence of a generally solved problem.

Across these twelve cases, Pearson correlation of SP gain per unordered sequence pair with reference-recall change is 0.110; Spearman is 0.210. The mean recall change is +0.385 percentage points, driven by the large small-family gain, while the median is -1.061 points. These are descriptive, unstable numbers from a small selected sample. They do not establish useful positive correlation or generalization. The frequent sign disagreement is the practical warning. All endpoints and losses are retained.

## Home-computer cost and sustained yield

The host was an Apple M2 with 24 GiB RAM, without a GPU. Complete new-method runs took approximately 1.2–388 seconds per family. Recorded peak Python process RSS was at most about 320 MB through the twelve full cases; additional-case RSS is the process maximum-so-far, not an isolated per-case measurement. Earlier selected/first-case runs lack RSS instrumentation. Other work ran concurrently, so timings are observational. This supports feasibility on a high-end home computer for these sizes; it does not establish Windows compatibility, thousand-sequence capacity, or long-protein scaling. The exact DP has a two-million-state limit and fails explicitly when exhausted.

The 91-sequence scaling probe increased SP from 333240 to 336396 after attempting only three rows: two exact moves improved the score, while the third exceeded the two-million-state budget and was recorded as a failure with no accepted proposal. Its DP stage took 42.41 seconds; the full baseline/legacy/DP pipeline took 314.26 seconds. Peak process RSS was 650.4 MB (cumulative high-water mark). Reference pair recall fell by 0.845 percentage points. This is a scaling observation, not a completed full-family search.

Three follow-ups ran to single-row coordinate optima: BB11001 reached 230, BB11029 reached -203, and BB20029 reached 28,715. Fresh reoptimization of every row independently confirmed all three endpoints. This does not prove global optimality. It does show that the easiest new operation has a finite supply of improvements: another donor repeating it on those endpoints has no remaining single-row gain.

The sustainable work queue should therefore emphasize distinct families, multi-row/block moves that escape those optima, verifier replication, objective/accuracy analysis, and stronger held-out baseline comparisons. Merely distributing more random seeds is unlikely to sustain exciting yield. A useful scientific direction is explaining which families benefit and why others deteriorate, then testing an independently specified improved model; changing penalties after inspecting these references would be a new experiment, not a better result under this frozen model.

## Assessment against the launch criteria

| Criterion | Assessment | Evidence / remaining issue |
|---|---|---|
| Early tangible progress | Strong for an experienced agent | First checked gain in about three minutes; 11/12 full cases improve SP. Novice replication remains untested. |
| Public demonstration | Promising with two visible measures | Sliding protein rows makes the task concrete. Show score and reference agreement together, including a failure example. |
| Meaningful biology | Not yet sufficient for a flagship claim | Only 2/12 beat the best baseline on reference pair recall; 8/12 lose recall versus the incumbent. |
| Home PC suitability | Strong at tested sizes | Seconds to minutes, hundreds of MB, no GPU. Larger instances need separate budgets. |
| Agent intelligence matters | Supported in this rehearsal | Reasoning about pair-specific affine histories enabled a stronger move than extending existing search. |
| Sustained donations | Conditional | Distinct families and stronger neighborhoods provide work; three cases saturate under single-row moves. |

A defensible public description is: **“Help us improve an alignment algorithm—and test whether its improvements recover biological correspondence.”** Avoid “each higher score is a biological discovery.” The paired positive/negative interactive examples make the scientific uncertainty understandable rather than hiding it.

Before promoting this to a biological flagship, I would require a bioinformatics reviewer, a larger independently chosen test bank, reproducible reference-accuracy gains against all strong baselines, and a defined review cadence. Prefer several independent contributor rehearsals starting from the newly improved candidates, because this run benefited from author context and a previously unimplemented operation. BAliBASE redistribution terms also remain unresolved for public distribution. Douglas is the named maintainer; his consent is not evidence of completed scientific review.

## Verification and reproduction

Run from the repository root, in an appropriately restricted local environment:

```sh
python3 scripts/verify.py
python3 research/contributor-30m/verify_trial.py
python3 research/contributor-30m/compare_biology.py
```

For deeper replay:

```sh
python3 scripts/replay.py
python3 research/contributor-30m/verify_trial.py --replay-case BB20029
python3 research/contributor-30m/verify_trial.py --replay-first
python3 research/contributor-30m/check_local_optima.py
```

`run_trial.py --dataset BB20029 --passes 2` regenerates the selected contribution and the roughly wall-time-matched control. Because time controls use whole batches, their final seed count can vary between machines. Exact DP outputs and recorded seed-specific operations are deterministic. Other original-family controls received only five seconds and are not runtime-matched comparisons.

`run_additional.py --mafft /path/to/mafft --famsa /path/to/famsa` regenerates the added families, with two single-thread runs of each baseline, three legacy-search seeds, and the row DP. Run it in a scratch checkout: generation overwrites that case's saved outputs. Original input/reference hashes, archive member names, tool commands, repeat hashes, source hashes and traces are retained. `converge.py --help` documents saturation runs. The mathematical model is unchanged from `docs/MODEL.md`: BLOSUM62, gap open 11, extension 1, penalized terminals, pairwise double gaps removed before gap-run accounting.

Checks cover exact scorer agreement with an independent run-length oracle, preserved residues/IDs, output hashes, acceptance chains, exhaustive tiny-row optima, 200 randomized tiny DNA profiles, 40 exhaustive protein-profile checks, deterministic ties, and explicit budget failures. The complete 58-row selected run was replayed. A separate pass checked every row of each claimed coordinate optimum. The original baseline/refinement portfolio's 59 runs were replayed too. `VERIFY.json` and retained logs give the final coverage counts.

`crosscheck_trial.py /path/to/bali_score_asan` compares trial endpoints with the original BAliBASE C evaluator, independently of the Python accuracy implementation. The existing source was compiled with AddressSanitizer because ordinary macOS builds trapped; this tooling limitation and the original build details are recorded in the base pilot. Three-decimal external outputs are compared within rounding tolerance, and gapped reference cores are rejected for this cross-check rather than silently using a different denominator.

Generation ran with network disabled and reference files denied. An early supplemental sandbox regex failed its access probe; that process was stopped, explicit per-file denies were added and successfully probed, and supplemental generation was restarted. The generator itself has no reference-reader or accuracy-selection path. The failed probe/log is retained. The current agent could see postgeneration evaluation, so this is reference-blind code, not a blinded researcher study.

The interactive example uses the actual accepted BB11029 and BB11015 snapshots and full-alignment metrics. The local browser preview was visually inspected, and both the family selector and refinement slider were exercised: the positive example shows -279 to -237 with 40.20% to 60.13% recall; the negative example shows 70 to 149 with 88.38% to 81.65% recall. An initial browser timeout resolved on a later inspection.
