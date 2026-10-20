# Sources and redistribution

BAliBASE: Thompson and collaborators; original R1–5 archive mirrored by the
University of Illinois MSA evaluation project. Preserve the citations and
`data/source/BAliBASE-README.txt`. The eight XML cases, derived FASTA files and
masks are kept here for local reproducibility. No explicit data redistribution
license was established in this session. Do not apply the project's MIT/CC
licenses to them. Review terms or use a fetch-only release before publication.
This does not block the user's requested LOCAL pilot.

BLOSUM62 numerical table: retrieved from the Biopython 1.86 data file at
https://raw.githubusercontent.com/biopython/biopython/biopython-186/Bio/Align/substitution_matrices/data/BLOSUM62
Header provenance is preserved. We copied the numerical table, not Biopython
implementation code. Its exact hash is in `results/generation-source.json`.

MAFFT 7.525: official source package; its license remains with the build tree.
FAMSA 2.5.2 and MUSCLE v5.3: GPL-3.0 upstream tools; no source or executable is
vendored in this repository. FAMSA is from an official release archive, not a
binary submitted as a research result. MUSCLE could not run because its macOS
release depends on a missing GCC11 runtime. Neither is represented as built
from source in this pilot. No global installation was performed.

BAliBASE's original bali_score 3.01 C sources were compiled outside the repo
using system Expat. Only evaluation logs and derived numeric comparisons are
stored here. Tool source/archive hashes and URLs are in `results/toolchain.json`.
