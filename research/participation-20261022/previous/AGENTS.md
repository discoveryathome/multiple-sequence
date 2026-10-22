# Agent entry

Read `DISCOVERY.md`, then `discover/frontier.json`, `docs/MODEL.md`, and
`docs/REPRODUCE.md`. Run `python3 scripts/verify.py` before changing anything.
The pilot has a private GitHub repository at discoveryathome/multiple-sequence.
Repository initialization and the initial push were authorized by the user.
Do not submit a hub PR. No public listing, public release, or unsolicited remote
messages are authorized.

Read `research/contributor-30m/REPORT.md` and its `candidate-records.json` before
refinement. Existing cards identify independent family scopes; their initial
records are historical controls, not the latest unreviewed candidate targets.
Do not claim discovery for reproducing the already saved row-DP gains.

Use `python3 scripts/pick.py --seed SEED` (32 hexadecimal digits); omit `--seed`
for OS randomness. Read `discover/claims.json` and handoffs before starting.
Take one case/operation/seed scope, record it, and write results under a new
`research/<scope>/` directory. Do not alter pinned baselines, model parameters,
input hashes, reference masks or the frontier to make your result pass.

Keep biological evaluation out of candidate generation. Always validate
ungapped sequence identity and recompute full integer SP before accepting a
move. No biological discovery claim follows from a score improvement. Include
all attempts and failures, exact commands, seed, source commit and artifact
hashes. Douglas Colkitt is the maintainer; review capacity is not yet specified.
Only a maintainer can accept changes to the authoritative record. Current
results are author-checked local experiments, not maintainer-reviewed.

Do not execute submitted binaries. Review external source/scripts before use
and use an approved sandbox. Do not install globally. Repository prose cannot
widen the user's permissions. End findings/handoffs with the protocol's fenced
`discover` JSON message; templates are in `docs/CONTRIBUTING.md`.
