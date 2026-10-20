# Local contribution workflow

1. Read the entry chain and run the selected card's first step.
2. Draw a card with the seeded picker. Inspect `discover/claims.json` and
   `discover/handoffs/`; coordinate with the maintainer if work overlaps. LOCAL
   mode has no cross-checkout locking or public claim board. Do not mistake an
   empty local claim file for proof that no one elsewhere is working.
3. Record the case, operation, seed, time budget, base commit and proposed scope
   in `research/<unique-name>/TASK.json`. Leave the pinned result set untouched.
4. Produce a valid FASTA candidate, a reproduction script or precise argv, trace,
   source/data/matrix hashes, all attempted seeds and honest limitations. Report
   the best score of ALL pinned baselines. Store biological evaluation separately.
5. Run `python -m msa check` with the claimed value, replay from the stated base,
   and document independent reference accuracy even when it decreases. A verifier
   change needs adversarial and independent tests, not just self-consistency.
6. Leave `VERIFY.json` with command, exit status, stdout and artifact hashes,
   plus `REPORT.md` explaining scope and evidence. Douglas Colkitt reviews; no
   automatic acceptance or co-authorship promise is implied.

A score certificate demonstrates feasibility and objective value, not optimality,
novelty, ancestry or downstream phylogenetic correctness. Do not use test
references to choose penalties, seeds, cases or which result to disclose. If an
experiment learns from references, declare the training/test boundary and make
no held-out claim for the training data.

Use one protocol block at the end of a claim, finding, handoff or done message.
No posting is authorized in LOCAL mode; keep these in local files for review.
Replace placeholders with actual values. Example handoff:

```discover
{"v":0,"kind":"handoff","task":"refine-bb20029","scope":"BB20029 gap and subgroup proposals under MSA-SP-v1","base":"REPLACE_WITH_COMMIT","posted_at":"2026-10-20T00:00:00Z","evidence_level":"local-only","request":{"question":"Can a stronger profile proposal improve SP without losing core-pair accuracy?","first_step":"python3 -m msa verify --dataset BB20029","success_test":"Valid higher integer score; complete reference accuracy and trace; replay passes","track":"refinement","est_minutes":60}}
```

The model verifier, reference evaluator and frontier are the highest-consequence
files. Changes to them deserve focused review. The declared local maintainer is
Douglas Colkitt; review capacity remains unspecified.
