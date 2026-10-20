"""Exact affine-SP placement of one sequence against a fixed alignment profile.

States (ins_mask,del_mask) describe the previous non-double-gap column in each
pair between the moving row and a fixed profile row. Other bits imply match.
M resets states to (profile_column_gap_mask,0). I resets all pairs to insertion.
D preserves states at profile gaps and sets deletion on profile residues.
Different histories with identical bitmasks are safely merged by max score.
"""
from pathlib import Path
import sys,time
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from msa.core import matrix,strip_empty,score,validate


def optimize_row(rows,key,model='protein',max_states=2000000):
    sub,op,ext=matrix(model)
    sequence=rows[key].replace('-','')
    profile=strip_empty({k:v for k,v in rows.items() if k!=key})
    ids=sorted(profile)
    cols=list(zip(*(profile[k] for k in ids)))
    width=len(cols);length=len(sequence);n=len(ids);all_bits=(1<<n)-1
    gaps=[sum(1<<k for k,c in enumerate(col) if c=='-') for col in cols]
    present=[all_bits^g for g in gaps]
    counts=[v.bit_count() for v in present]
    gapcounts=[n-v for v in counts]
    emissions={a:[sum(sub[a,c] for c in col if c!='-') for col in cols] for a in set(sequence)}
    cells=[[{} for _ in range(width+1)] for _ in range(length+1)]
    cells[0][0][(0,0)]=(0,None,None)
    created=1;visited=0
    def update(i,j,state,value,prev,move):
        nonlocal created
        old=cells[i][j].get(state)
        if old is None:
            created+=1
            if created>max_states:raise RuntimeError('exact row DP state budget exceeded; no approximate result returned')
        if old is None or value>old[0]:cells[i][j][state]=(value,prev,move)
    for i in range(length+1):
        for j in range(width+1):
            cell=cells[i][j]
            for state in sorted(cell):
                visited+=1
                ins,delete=state;value=cell[state][0]
                if i<length and j<width:
                    extensions=(ins&gaps[j]).bit_count()
                    delta=emissions[sequence[i]][j]-extensions*ext-(gapcounts[j]-extensions)*op
                    update(i+1,j+1,(gaps[j],0),value+delta,state,'M')
                if j<width:
                    extensions=(delete&present[j]).bit_count()
                    delta=-extensions*ext-(counts[j]-extensions)*op
                    update(i,j+1,(ins&gaps[j],delete|present[j]),value+delta,state,'D')
                if i<length:
                    extensions=ins.bit_count()
                    delta=-extensions*ext-(n-extensions)*op
                    update(i+1,j,(all_bits,0),value+delta,state,'I')
    state=min(cells[length][width],key=lambda s:(-cells[length][width][s][0],s))
    cross=cells[length][width][state][0]
    result={k:[] for k in sorted(rows)}
    i,j=length,width
    while i or j:
        _,prev,move=cells[i][j][state]
        result[key].append(sequence[i-1] if move in ('M','I') else '-')
        for k in ids:result[k].append(profile[k][j-1] if move in ('M','D') else '-')
        if move in ('M','I'):i-=1
        if move in ('M','D'):j-=1
        state=prev
    result={k:''.join(reversed(v)) for k,v in result.items()}
    validate({k:v.replace('-','') for k,v in rows.items()},result,model)
    expected=cross+(score(profile,model) if len(profile)>1 else 0)
    actual=score(result,model)
    if expected!=actual:raise AssertionError(('DP/full-score mismatch',expected,actual))
    if actual<score(rows,model):raise AssertionError('exact row optimum below feasible input')
    return result,dict(cross_score=cross,total_score=actual,states=created,visited=visited,max_cell_states=max(len(c) for row in cells for c in row))
