# Historical session driver; paths assume the original workspace layout.
# Portable reproduction: run_trial.py --dataset CASE --passes 1 --control-seconds 5
import subprocess,json,time,datetime
from pathlib import Path
root=Path(__file__).resolve().parent
records=[]
for case in ['BB11001','BB11015','BB12021','BB20030','BB30027','BB40010','BB50013']:
    start=time.monotonic()
    command=['sandbox-exec','-f',str(root/'refinement.sb'),'python3',str(root/'repo/research/contributor-30m/run_trial.py'),'--dataset',case,'--passes','1','--control-seconds','5']
    with (root/(case+'.log')).open('w') as log:
        run=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
    record=dict(case=case,exit_code=run.returncode,elapsed=time.monotonic()-start,finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
    records.append(record);(root/'cohort-status.json').write_text(json.dumps(records,indent=2)+'\n')
    print(record,flush=True)
