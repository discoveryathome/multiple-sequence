# Local preparation handoff

Read [README.md](README.md), [REVIEW.md](REVIEW.md) and [EVALUATION.md](EVALUATION.md).
The preparation is author-checked and committed locally. Scientific review,
confirmation and public intake remain pending; no external message was sent.

The manifest verifies the preparation base before starting a contribution.
Intentional candidate-code edits belong in a new commit with their own source
bindings; do not rewrite the base manifest to hide an intended or accidental change.

```discover
{"v":0,"kind":"handoff","scope":"msa: preparation for scoped computational contributor trials; versioned inherited controls, validation and outside-review package","base":"130d8fb2bd4d8be8bd7191c3cbf4456cf6ee4806","posted_at":"2026-10-21T16:16:46.054943+00:00","evidence_level":"local-only","request":{"question":"Review scientific assumptions, future evaluation design and intake prerequisites in REVIEW.md and EVALUATION.md.","first_step":"python3 scripts/readiness.py check --dataset BB11015","success_test":"Return exact commit/hashes, checks, limitations, review capacity and a scoped decision. No independent review is assumed."}}
```
