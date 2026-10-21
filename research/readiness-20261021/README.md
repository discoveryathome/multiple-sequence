# Multiple-sequence alignment: preparation for scoped trials

Local preparation authorized on 2026-10-21. Results are author-checked; scientific
review and public intake remain pending. No external messages or publication occurred.

## Start

From the repository root in its documented environment:

```sh
python3 scripts/readiness.py check --dataset BB11015
```

## Prepared work

All 13 saved contributor candidates (12 full-family cases and one scaling probe) and
39 baseline alignments were rechecked with both exact scorers and input validation.
`portfolio.json` binds each input, reference, incumbent, model and baseline. The
three single-row coordinate optima are removed from ordinary refinement draws;
a separate multi-row/verification task covers them. The previous profile-objective
mismatch has already been addressed and is no longer presented as an unimplemented task.

`starts.json` contains only sequence/score starting information; the reference
metrics stay in the separate diagnostic portfolio. `check` validates a candidate and reports its gain over the inherited candidate
without reading references. `evaluate` is a separate, post-generation diagnostic:

```sh
python3 scripts/readiness.py check --dataset BB11015 --candidate /path/to/candidate.fa
python3 scripts/readiness.py evaluate --dataset BB11015 --candidate /path/to/candidate.fa
```

Both commands cover the added trial families as well as the original eight. A valid
higher score is an optimization result. Falling reference accuracy remains visible;
it is not scientific improvement merely because it passes the exact scorer.
Historical accepted/proposed distinctions in `discover/frontier.json` are unchanged.

A proposed reserve contains **10 additional families across all six categories**.
Only full-length unaligned sequence files were read to select them; no reference
outcomes were evaluated. The first small-size inventory supplied only four cases
in two categories, so the input-only size limit was expanded to 50 sequences and
600 residues before any outcome inspection. Both inventories are retained. Exact
sequence and 6-mer overlap screens reduce obvious duplication; they do not prove
homology independence. The reserve contains metadata/hashes only, not newly bundled
sequence or reference files. See [EVALUATION.md](EVALUATION.md).

## Review and trials

Read [REVIEW.md](REVIEW.md), [EVALUATION.md](EVALUATION.md), and [TRIAL.md](TRIAL.md).
The unfilled `review.json` is intentional. A reviewer must identify the exact commit
and artifact hashes. Independent human review is not inferred from multiple checkers.

Remaining gates:

- Bioinformatics reviewer for objective/accuracy interpretation and acceptance rules.
- Independent curator for reserve-family homology and a second benchmark.
- Explicit benchmark redistribution resolution before public distribution.
- Named review capacity and independent contributor trials.
