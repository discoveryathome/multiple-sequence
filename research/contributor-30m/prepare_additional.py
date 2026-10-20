import json,tarfile,pathlib,xml.etree.ElementTree as E,hashlib,datetime,argparse
p=argparse.ArgumentParser();p.add_argument('--archive',required=True);p.add_argument('--output',required=True);a=p.parse_args()
R=pathlib.Path(a.output);R.mkdir(parents=True,exist_ok=True)
selected=[('RV11','BB11029','unseen-small'),('RV12','BB12040','unseen-small'),('RV30','BB30017','unseen-medium'),('RV50','BB50007','unseen-medium'),('RV20','BB20036','scaling-probe')]
records=[]
with tarfile.open(a.archive) as t:
 for group,name,role in selected:
  member=f'bb3_release/{group}/{name}.xml';raw=t.extractfile(member).read();x=E.fromstring(raw)
  ref={s.findtext('seq-name').strip():''.join(s.findtext('seq-data').split()).upper() for s in x.findall('.//sequence')}
  core=[int(v)==1 for c in x.findall('.//column-score') if c.findtext('colsco-name')=='coreblock' for v in c.findtext('colsco-data').split()]
  folder=R/name;folder.mkdir(exist_ok=True)
  for label,rows in [('input',{k:s.replace('-','') for k,s in ref.items()}),('reference',ref)]:
   (folder/(label+'.fa')).write_text(''.join('>'+k+'\n'+rows[k]+'\n' for k in sorted(rows)))
  (folder/'reference.xml').write_bytes(raw);(folder/'core.json').write_text(json.dumps(core)+'\n')
  records.append(dict(id=name,category=group,role=role,n=len(ref),max_length=max(len(s.replace('-','')) for s in ref.values()),core_columns=sum(core),source_member=member,sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [folder/n for n in ['input.fa','reference.fa','reference.xml','core.json']]}))
(R/'manifest.json').write_text(json.dumps(dict(selected_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),selection='Chosen from inventory by size/category without evaluating accuracy; four unseen cases and one 91-sequence scaling probe. Not a random representative sample.',records=records),indent=2)+'\n')
print(json.dumps(records,indent=2))
