#!/usr/bin/env python3
"""Extract only selected data members; never execute archive contents."""
import sys,json,tarfile,xml.etree.ElementTree as ET
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from msa.core import write_fasta,validate,digest
ROOT=Path(__file__).resolve().parents[1]
SELECTED=[('RV11','BB11001','development'),('RV11','BB11015','evaluation'),
          ('RV12','BB12021','development'),('RV20','BB20029','evaluation'),
          ('RV20','BB20030','evaluation'),('RV30','BB30027','evaluation'),
          ('RV40','BB40010','development'),('RV50','BB50013','evaluation')]
URL='https://publish.illinois.edu/msaevaluation/files/2017/07/BAliBASE_R1-5.tar_.gz'

def main(archive):
    records=[]
    with tarfile.open(archive) as tar:
        for group,name,split in SELECTED:
            member=f'bb3_release/{group}/{name}.xml'
            raw=tar.extractfile(member).read()
            root=ET.fromstring(raw)
            reference={s.findtext('seq-name').strip():''.join(s.findtext('seq-data').split()).upper()
                       for s in root.findall('.//sequence')}
            masks=[c for c in root.findall('.//column-score') if c.findtext('colsco-name')=='coreblock']
            assert len(masks)==1
            core=[int(x)==1 for x in masks[0].findtext('colsco-data').split()]
            assert len(core)==len(next(iter(reference.values()))) and any(core)
            inputs={k:s.replace('-','') for k,s in reference.items()}
            validate(inputs,reference)
            paths={'input':f'data/inputs/{name}.fa','reference':f'data/references/{name}.fa',
                   'mask':f'data/references/{name}.core.json','xml':f'data/source/{name}.xml'}
            write_fasta(ROOT/paths['input'],inputs);write_fasta(ROOT/paths['reference'],reference)
            (ROOT/paths['mask']).write_text(json.dumps(core)+'\n');(ROOT/paths['xml']).write_bytes(raw)
            records.append(dict(id=name,category=group,split=split,n=len(inputs),
                                max_length=max(map(len,inputs.values())),reference_columns=len(core),core_columns=sum(core),
                                source_member=member,source_alignment_name=root.findtext('.//aln-name'),
                                **paths,sha256={k:digest(ROOT/p) for k,p in paths.items()}))
        (ROOT/'data/source/BAliBASE-README.txt').write_bytes(tar.extractfile('bb3_release/README').read())
    manifest=dict(source_url=URL,archive_sha256=digest(archive),selection='Intact full-length families; chosen by category and size before scoring. No sequence subsampling.',datasets=records)
    (ROOT/'data/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps([{k:r[k] for k in ('id','category','split','n','max_length','core_columns')} for r in records],indent=2))
if __name__=='__main__': main(sys.argv[1])
