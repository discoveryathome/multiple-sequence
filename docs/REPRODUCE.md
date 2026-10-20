# Reproduction

Use Python 3.9+ and run from the repository root. No pip install, network, or
external alignment executable is needed to verify saved results.

```sh
python3 scripts/verify.py
python3 scripts/replay.py
```

The first command recomputes exact model scores, all reference metrics and the
primary summary, checks source/data/baseline/candidate hashes and negative
controls. It checks the stored original-evaluator comparison record; it does
not pretend to execute the external evaluator. The second command regenerates
all 56 main refinement experiments, including rejected-proposal traces. On the
pilot machine the full main search takes a few minutes; timings are descriptive
and can vary with other activity. A per-family first step is much shorter:

```sh
python3 -m msa verify --dataset BB20029
python3 scripts/replay.py --dataset BB11001
```

To check a new candidate or a claimed score:

```sh
python3 -m msa check --dataset BB11001 --alignment results/baselines/BB11001.mafft-linsi.fa
python3 -m msa check --dataset BB11001 --alignment results/baselines/BB11001.mafft-linsi.fa --claimed-score 999999
```

The second command MUST exit nonzero. New searches can write to `scratch/`:

```sh
python3 -m msa refine --dataset BB20029 --alignment results/baselines/BB20029.mafft-ginsi.fa --seed 42 --rounds 10 --out scratch/BB20029.s42.fa
```

Always compare to the largest score among all three baselines, not whichever
baseline happened to be passed to the command. The manifest fixes input hashes.
Changing a matrix, penalty, terminal-gap convention, sequence subset or input
sequence creates a different model/case and cannot replace a current record.

## Regenerate external methods

Install MAFFT 7.525 and FAMSA 2.5.2 locally by their official instructions. Source
builds or official release packages must be reviewed and sandboxed; do not run
binaries supplied inside a donor result package. No global installation is
required. This pilot built MAFFT from source and used FAMSA's official macOS
arm64 release package; binaries/build trees are outside this repository.
`results/toolchain.json` pins URLs, downloaded hashes and platform details.

```sh
python3 scripts/run_baselines.py /PATH/TO/mafft scratch/baselines
python3 scripts/run_famsa.py /PATH/TO/famsa scratch/baselines
python3 scripts/compare_baselines.py scratch/baselines
```

Commands and exact canonical output hashes are in the baseline provenance JSON
files. Each script executes every case twice. One thread is fixed. Canonical
hashes sort IDs and normalize FASTA case and wrapping. Cross-platform equality
is a check to perform, not a promise. A mismatch must be investigated rather
than silently replacing the pinned baseline outputs.

To rebuild original data: fetch the archive URL in `data/manifest.json`, confirm
its SHA-256, and run `python3 scripts/prepare_data.py /PATH/TO/archive.tar.gz`.
Only eight selected XML members and the archive README are extracted. The
converter does not execute any bundled code. Data are not relicensed by us.

To rerun the original BAliBASE accuracy cross-check, extract only `bali_score_src`
C sources from that archive, screen and review them, and compile with a C
compiler and Expat (no need for its bundled precompiled objects). The pilot used:

```sh
cc -std=gnu89 -Wno-implicit-function-declaration -g -O0 -fsanitize=address readxml.c init.c util.c bali_score.c -lexpat -lm -o bali_score
python3 scripts/crosscheck_bali.py /PATH/TO/bali_score scratch/bali-crosscheck
```

The unmodified legacy C program trapped in non-sanitizer builds on this macOS
host; the recorded run uses the AddressSanitizer build above. No source patch
was needed. Other platforms should record their own compiler configuration.

Compare `scratch/bali-crosscheck/crosscheck.json` with the pinned cross-check.
The original program prints pair accuracy to three decimals; tolerance is
0.000501. Strict TC and its counts are computed separately, since legacy TC
truncates. References score 1 against themselves. This is an empirical evaluator
cross-check on these cases, not a formal proof covering arbitrary alignments.

## Recreate experiments and evaluation

```sh
python3 scripts/run_experiments.py --out scratch/experiments
python3 scripts/replay.py
```

`experiment.json` defines the main search and four single-operation controls.
The saved experiment source hashes document the generation code. `scripts/extended.py`
recreates three longer searches (seed 101, 12 rounds) from the best combined
main candidates; it writes `results/extended`, so run in a disposable copy.
`python3 scripts/evaluate.py --check` recomputes reports without overwriting them.
Remove `--check` only when intentionally making a new, reviewed result set.

Recorded generation was reference-blind both in code and via explicit sandbox
read denials for the reference and XML directories. That is a local execution
property, not a security claim about agents who can edit the sandbox profile.
