import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from msa.core import ROOT,canonical_hash,read_fasta
out=Path(sys.argv[1])
n=0
for name in ['provenance.json','famsa-provenance.json']:
    for r in json.loads((ROOT/'results/baselines'/name).read_text())['records']:
        if canonical_hash(read_fasta(out/r['alignment']))!=r['canonical_sha256']:raise ValueError('baseline differs: '+r['alignment'])
        n+=1
print('BASELINE REPLAY PASS',n)
