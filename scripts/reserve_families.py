"""Choose a proposed evaluation bank using unaligned sequences only.

Writes metadata and content hashes, not benchmark sequences or references.
No reference XML/core mask or alignment quality is opened or used in selection.
"""
import argparse,hashlib,json,re,sys,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from msa.core import digest,read_fasta,canonical_hash
OUT=ROOT/'research/readiness-20261021';SEED='20261021-bio-reserve-v1'
def sequences(text):
    rows={};name=None
    for line in text.splitlines():
        line=line.strip()
        if not line:continue
        if line.startswith('>'):
            name=line[1:].split()[0]
            if name in rows:raise ValueError('Duplicate ID')
            rows[name]=''
        else:
            if name is None:raise ValueError('Missing FASTA header')
            rows[name]+=line.upper()
    if any(not s or set(s)-set('ARNDCQEGHILKMFPSTWYVBZX') for s in rows.values()):raise ValueError('Invalid unaligned protein')
    return rows
def kmers(s):return {s[i:i+6] for i in range(max(0,len(s)-5))}
def overlaps(rows,known):
    for s in rows.values():
        a=kmers(s)
        for other,b in known:
            if s==other or (a and b and len(a&b)/len(a|b)>=.2):return True
    return False
def reserve(archive):
    original=json.loads((ROOT/'data/manifest.json').read_text())
    if digest(archive)!=original['archive_sha256']:raise ValueError('Wrong source archive')
    portfolio=json.loads((OUT/'portfolio.json').read_text());known=[];exposed={c['dataset'] for c in portfolio['cases']}
    for c in portfolio['cases']:
        known.extend((s,kmers(s)) for s in read_fasta(ROOT/c['input']).values())
    selected=[];excluded={};counts={}
    with tarfile.open(archive) as t:
        names=[n for n in t.getnames() if re.fullmatch(r'bb3_release/RV\d+/BB\d+\.tfa',n)]
        names.sort(key=lambda n:hashlib.sha256((SEED+n).encode()).hexdigest())
        for name in names:
            case=Path(name).stem;category=Path(name).parent.name
            if case in exposed:continue
            raw=t.extractfile(name).read()
            try:rows=sequences(raw.decode())
            except ValueError:excluded['invalid_alphabet']=excluded.get('invalid_alphabet',0)+1;continue
            if not 4<=len(rows)<=50 or not 60<=max(map(len,rows.values()))<=600:continue
            if counts.get(category,0)>=2:continue
            if overlaps(rows,known):excluded['sequence_overlap_screen']=excluded.get('sequence_overlap_screen',0)+1;continue
            selected.append(dict(dataset=case,category=category,source_member=name,n=len(rows),max_length=max(map(len,rows.values())),unaligned_member_sha256=hashlib.sha256(raw).hexdigest(),canonical_input_sha256=canonical_hash(rows)))
            known.extend((s,kmers(s)) for s in rows.values());counts[category]=counts.get(category,0)+1
    result=dict(version=1,seed=SEED,source_url=original['source_url'],archive_sha256=original['archive_sha256'],cases=selected,category_counts=counts,exclusions=excluded,
      status='Proposed reserve only; reference outcomes unopened; independent curator and redistribution decisions pending.',
      selection='Full-length unaligned .tfa inputs only. Deterministic hash order, up to two per category, 4–50 sequences, maximum length 60–600; exclude all exposed cases and exact/6-mer-Jaccard>=0.2 sequence overlap.',
      limitations='The overlap screen is heuristic and does not prove homology-disjoint families. Inputs are public, so this is not a private or independently selected test set. No quality results have been measured.')
    (OUT/'reserved-families.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
def main():
    p=argparse.ArgumentParser();p.add_argument('--archive');p.add_argument('--check',action='store_true');a=p.parse_args()
    if a.check:
        r=json.loads((OUT/'reserved-families.json').read_text());assert r['cases'] and len({c['dataset'] for c in r['cases']})==len(r['cases'])
        assert not {c['dataset'] for c in r['cases']}&{c['dataset'] for c in json.loads((OUT/'portfolio.json').read_text())['cases']}
        print('PASS',len(r['cases']),'proposed reserve identifiers; no reference outcomes evaluated')
    elif a.archive:reserve(a.archive)
    else:p.error('--archive or --check required')
if __name__=='__main__':main()
