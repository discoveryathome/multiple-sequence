# Literature and claim audit (2026-10-20)

This is an optimization and benchmark pilot, not a claim to the world's best
alignment algorithm. There is no meaningful universal best alignment without
specifying sequences, a scoring model, and an evaluation target.

| Source | Verified relevance and limit |
| --- | --- |
| [MAFFT algorithm documentation](https://mafft.ddbj.nig.ac.jp/alignment/software/algorithms/) | L-INS-i and G-INS-i combine weighted pair scoring with consistency information. Their objectives differ from our unweighted external SP objective. |
| [Katoh et al., 2005](https://doi.org/10.1093/nar/gki198) | Describes iterative improvement and group-to-group realignment. Supports subgroup/profile proposals; does not establish the performance of our implementation. |
| [MAFFT source releases](https://mafft.cbrc.jp/alignment/software/source.html) | Version 7.525 is the pinned source release used here. L-INS-i and G-INS-i with 1,000 refinement iterations are substantial baselines. |
| [Edgar, MUSCLE5, 2022](https://doi.org/10.1038/s41467-022-34630-w) | High-accuracy ensemble approach illustrates sensitivity to model and guide-tree choices. A useful independent baseline; our v5.3 macOS attempt could not load its GCC11 runtime, so we claim no MUSCLE reproduction. |
| [FAMSA2, Nature Biotechnology, 2026](https://doi.org/10.1038/s41587-026-03095-3) and [official code](https://github.com/refresh-bio/FAMSA) | Current independent method with emphasis on large protein collections. We run release 2.5.2, not extrapolate its published large-scale performance to these small cases. |
| [BAliBASE 3.0, Thompson et al., 2005](https://doi.org/10.1002/prot.20527) | Reference database underlying this study. Original archive annotations and README provide our category and core definitions. |
| [Illinois BAliBASE mirror](https://publish.illinois.edu/msaevaluation/balibase-benchmark-alignment-files/) | Its processed FASTA collection renames and samples large alignments. We instead take intact original XML cases from its R1–5 archive, retaining core annotations and original IDs. |
| [Edgar, Quality measures for protein alignment benchmarks, 2010](https://pmc.ncbi.nlm.nih.gov/articles/PMC2853116/) | Reports problems in structure-based reference benchmarks. Reference agreement is evidence under the benchmark, not unquestionable evolutionary truth. |
| [Wang and Jiang, 1994](https://doi.org/10.1089/cmb.1994.1.337) | Establishes NP-completeness of the general SP-alignment problem. We do not infer a new hardness theorem for this particular fixed matrix and gap convention. |
| [Benchmark collection](https://www.drive5.com/bench/) | PREFAB, OXBENCH and SABRE are candidates for independent follow-up. They have not been imported or evaluated here. |

The user's proposed task is feasible as a search-and-verification pilot.
Conventional and modern aligners already solve useful approximate versions;
our question is whether a reference-blind refinement can improve a precisely
fixed external model starting from strong outputs, and what accuracy changes
accompany those gains. That narrower question is not settled by running an
aligner once.

Claim audit: public BAliBASE files and core annotations—confirmed by download,
XML conversion and hashes. Conventional reproducibility—tested by two runs per
method/case. Exact values—locally checked by two implementations. Score gain
implies biological gain—unsupported, explicitly excluded. Universal superiority,
novel algorithms, global optimality, and maintained donor review—NOT claimed.

Settled within this pilot: comparing against a deliberately bad alignment says
little about useful progress; pooling raw SP values across family sizes is not
a biological analysis; fitting penalties against test references invalidates
an independent evaluation; exact score arithmetic does not certify the model's
biological validity. The profile DP's linear surrogate is not an affine-MSA
optimality certificate. These are limits, not open tasks to rediscover.

Follow-up datasets should include independent families and an independent
benchmark collection. BAliBASE categories are difficulty types, not a guarantee
of phylogenetic independence. The development/evaluation labels in our manifest
do not establish a homolog-disjoint split or erase past community benchmark use.
