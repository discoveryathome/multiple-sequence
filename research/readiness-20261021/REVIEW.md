# Review package: Multiple-sequence alignment

Prepared locally; not sent. Base commit: `130d8fb2bd4d8be8bd7191c3cbf4456cf6ee4806`.
Review the final preparation commit and artifact manifest, then run the commands
in README.md and the negative controls in the project tests.

1. Audit the pair-projected affine score and exact row-DP assumptions, and verify the inherited candidate/control metrics.
2. Which useful biological-method questions can be tested without selecting against the exposed references? Review EVALUATION.md as a proposed new formulation.
3. Audit reserve-family homology, category balance and appropriate external benchmarks. The sequence-only overlap heuristic is not sufficient proof.
4. Resolve data redistribution and approve an intake scope plus review capacity.

Return the reviewed commit, artifact hashes, commands, findings, conflicts/prior
involvement, proposed fixes, decision (revise / approve scoped trial / defer), and
review capacity. Fill review.json only after actual review.
