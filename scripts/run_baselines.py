#!/usr/bin/env python3
"""Regenerate MAFFT baselines, twice, and compare canonical outputs exactly."""
import sys,json,subprocess,time,platform
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from msa.core import read_fasta,write_fasta,validate,digest,canonical_hash
ROOT=Path(__file__).resolve().parents[1]

def main(binary,out):
    binary=str(Path(binary).resolve()); out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    version=subprocess.run([binary,'--version'],capture_output=True,text=True,check=True)
    version=(version.stdout+version.stderr).strip()
    records=[]
    for d in json.loads((ROOT/'data/manifest.json').read_text())['datasets']:
        inp=ROOT/d['input']
        for method,flag in [('mafft-linsi','--localpair'),('mafft-ginsi','--globalpair')]:
            command=[binary,'--thread','1','--amino',flag,'--maxiterate','1000','--inputorder',str(inp)]
            hashes=[];times=[]
            for repeat in range(2):
                start=time.monotonic();run=subprocess.run(command,capture_output=True,text=True,check=True,timeout=180)
                times.append(time.monotonic()-start)
                path=out/f'{d["id"]}.{method}.repeat{repeat}.fa';path.write_text(run.stdout)
                rows=read_fasta(path);validate(read_fasta(inp),rows)
                hashes.append(canonical_hash(rows))
                (out/f'{d["id"]}.{method}.repeat{repeat}.log').write_text(run.stderr)
                if repeat==0: write_fasta(out/f'{d["id"]}.{method}.fa',rows)
                path.unlink()
            assert hashes[0]==hashes[1], 'baseline replay changed'
            records.append(dict(dataset=d['id'],method=method,version=version,
                                argv=['mafft',*command[1:-1],d['input']],input_sha256=digest(inp),
                                alignment=f'{d["id"]}.{method}.fa',canonical_sha256=hashes[0],
                                repeat_hashes=hashes,seconds=times))
            print(d['id'],method,hashes[0][:12],flush=True)
    (out/'provenance.json').write_text(json.dumps(dict(platform=platform.platform(),records=records),indent=2)+'\n')
if __name__=='__main__': main(sys.argv[1],sys.argv[2])
