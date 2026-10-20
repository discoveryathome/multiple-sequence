#!/usr/bin/env python3
"""Protocol draw, with local live-claim filtering; no network and no posting."""
import argparse,json,secrets,re
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--seed');a=p.parse_args()
seed=a.seed or secrets.token_hex(16)
if not re.fullmatch('[0-9a-fA-F]{32}',seed):p.error('seed must be 32 hex digits')
catalog=json.loads((ROOT/'discover/catalog.json').read_text())
tracks=catalog['tracks'];draw=int(seed[:8],16)%sum(t['weight'] for t in tracks)
for track in tracks:
    if draw<track['weight']:break
    draw-=track['weight']
claims=json.loads((ROOT/'discover/claims.json').read_text());now=datetime.now(timezone.utc)
live=[c for c in claims if datetime.fromisoformat(c['expires'].replace('Z','+00:00'))>now]
blocked={c['task'] for c in live}
cards=[c for c in track['tasks'] if c['id'] not in blocked]
if not cards:
    print(json.dumps(dict(seed=seed,track=track['id'],status='all local cards claimed',live_claims=live)));raise SystemExit(2)
card=cards[int(seed[8:16],16)%len(cards)]
print(json.dumps(dict(seed=seed,track=track['id'],task=card['id'],question=card['question'],first_step=card['first_step'],live_claims=live,coordination='local advisory only; no cross-checkout locking'),indent=2))
