#!/usr/bin/env python3
"""Run the independent modern FAMSA2 baseline twice, one thread."""
import sys,json,subprocess,time,platform
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from msa.core import *
ROOT=Path(__file__).resolve().parents[1]
def main(binary,out):
    binary=str(Path(binary).resolve());out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    help_run=subprocess.run([binary,'-h'],capture_output=True,text=True)
    version=(help_run.stdout+help_run.stderr).splitlines()[:4]
    records=[]
    for d in json.loads((ROOT/'data/manifest.json').read_text())['datasets']:
        inp=ROOT/d['input'];hashes=[];times=[]
        for repeat in range(2):
            path=out/f'{d["id"]}.famsa2.repeat{repeat}.fa'
            command=[binary,'-t','1',str(inp),str(path)]
            start=time.monotonic();run=subprocess.run(command,capture_output=True,text=True,check=True,timeout=180)
            times.append(time.monotonic()-start);rows=read_fasta(path);validate(read_fasta(inp),rows)
            hashes.append(canonical_hash(rows))
            (out/f'{d["id"]}.famsa2.repeat{repeat}.log').write_text(run.stdout+run.stderr)
            if repeat==0:write_fasta(out/f'{d["id"]}.famsa2.fa',rows)
            path.unlink()
        assert hashes[0]==hashes[1]
        records.append(dict(dataset=d['id'],method='famsa2',version=version,argv=['famsa','-t','1',d['input'],'OUTPUT'],
                            input_sha256=digest(inp),alignment=f'{d["id"]}.famsa2.fa',canonical_sha256=hashes[0],repeat_hashes=hashes,seconds=times))
        print(d['id'],hashes[0][:12],flush=True)
    (out/'famsa-provenance.json').write_text(json.dumps(dict(platform=platform.platform(),records=records),indent=2)+'\n')
if __name__=='__main__':main(sys.argv[1],sys.argv[2])
