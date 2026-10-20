"""Reference-blind proposals with exact full-affine-score acceptance."""
from collections import Counter
from random import Random
from .core import matrix, score, strip_empty, validate, canonical_hash


def profile_align(left, right, model='protein', gap_cost=4):
    """Exact DP for a LINEAR cross-profile surrogate, not for affine SP.

    Internal profile columns are preserved. Existing gaps score -gap_cost per
    residue-gap; gap-gap is zero. Final acceptance always uses full affine SP.
    Tie order: diagonal, consume-left, consume-right.
    """
    left,right = strip_empty(left),strip_empty(right)
    li,ri = sorted(left),sorted(right)
    lc,rc = list(zip(*(left[k] for k in li))),list(zip(*(right[k] for k in ri)))
    a,b = len(lc),len(rc)
    sub,_,_ = matrix(model)
    def val(x,y):
        return 0 if x == y == '-' else -gap_cost if '-' in (x,y) else sub[x,y]
    lct,rct = [Counter(c) for c in lc],[Counter(c) for c in rc]
    # Score a left column against each possible right residue just once.
    alphabet = sorted({x for c in rc for x in c})
    lookup = [{y:sum(n*val(x,y) for x,n in c.items()) for y in alphabet} for c in lct]
    lg = [-gap_cost*sum(x != '-' for x in c)*len(ri) for c in lc]
    rg = [-gap_cost*sum(x != '-' for x in c)*len(li) for c in rc]
    trace = [bytearray(b+1) for _ in range(a+1)]
    prev = [0]*(b+1)
    for j in range(1,b+1):
        prev[j] = prev[j-1]+rg[j-1]
        trace[0][j] = 2
    for i in range(1,a+1):
        cur = [prev[0]+lg[i-1]]+[0]*b
        trace[i][0] = 1
        lookup_i = lookup[i-1]
        for j in range(1,b+1):
            cross = sum(n*lookup_i[y] for y,n in rct[j-1].items())
            options = (prev[j-1]+cross,prev[j]+lg[i-1],cur[j-1]+rg[j-1])
            best = max(options)
            cur[j],trace[i][j] = best,options.index(best)
        prev = cur
    out = {k:[] for k in li+ri}
    i,j = a,b
    while i or j:
        move = trace[i][j]
        for k in li:
            out[k].append(left[k][i-1] if move != 2 else '-')
        for k in ri:
            out[k].append(right[k][j-1] if move != 1 else '-')
        i -= move != 2
        j -= move != 1
    return {k:''.join(reversed(v)) for k,v in out.items()}


def progressive(rows, order, model):
    out = {order[0]:rows[order[0]].replace('-','')}
    for k in order[1:]:
        out = profile_align(out,{k:rows[k].replace('-','')},model)
    return out


def propose(rows, operation, rng, model):
    ids = sorted(rows)
    if operation == 'profile':
        # Remove one row and optimize its placement against the other profile.
        k = rng.choice(ids)
        return profile_align({k:rows[k]}, {j:rows[j] for j in ids if j != k}, model)
    if operation == 'subgroup':
        # A residue-agreement split avoids relying solely on arbitrary partitions.
        anchor = rng.choice(ids)
        ranked = sorted(ids,key=lambda k:(-sum(a==b and a!='-' for a,b in zip(rows[k],rows[anchor])),k))
        chosen = set(ranked[:max(1,len(ids)//2)])
        return profile_align({k:rows[k] for k in ids if k in chosen},
                             {k:rows[k] for k in ids if k not in chosen},model)
    if operation == 'block':
        # Rank model-discordant windows; never look at reference positions.
        length = len(rows[ids[0]])
        width = min(40,length)
        windows = []
        for start in range(0,max(1,length-width+1),max(1,width//2)):
            part = {k:rows[k][start:start+width] for k in ids}
            windows.append((score(part,model),start))
        windows.sort()
        start = rng.choice(windows[:min(4,len(windows))])[1]
        end = start+width
        order = ids[:]
        rng.shuffle(order)
        part = progressive({k:rows[k][start:end] for k in ids},order,model)
        return strip_empty({k:rows[k][:start]+part[k]+rows[k][end:] for k in ids})
    if operation == 'gap':
        # Move a complete gap run across one adjacent residue, preserving order.
        possibilities = []
        for k in ids:
            s = rows[k]
            i = 0
            while i < len(s):
                if s[i] != '-':
                    i += 1
                    continue
                end = i+1
                while end<len(s) and s[end]=='-': end+=1
                if i: possibilities.append((k,i,end,-1))
                if end<len(s): possibilities.append((k,i,end,1))
                i = end
        if not possibilities:
            return dict(rows)
        # Best of a deterministic, seeded sample; all evaluations use the model.
        options = rng.sample(possibilities,min(16,len(possibilities)))
        best,best_score = dict(rows),score(rows,model)
        for k,i,end,d in options:
            s = rows[k]
            if d<0: s=s[:i-1]+s[i:end]+s[i-1]+s[end:]
            else: s=s[:i]+s[end]+s[i:end]+s[end+1:]
            candidate=strip_empty({**rows,k:s})
            value=score(candidate,model)
            if value>best_score: best,best_score=candidate,value
        return best
    raise ValueError('unknown operation')


def refine(inputs, initial, seed=0, rounds=3, operations=('block','subgroup','gap','profile'),model='protein'):
    validate(inputs,initial,model)
    rows=dict(initial)
    current=score(rows,model)
    rng=Random(seed)
    trace=[]
    for iteration in range(rounds):
        for operation in operations:
            candidate=strip_empty(propose(rows,operation,rng,model))
            validate(inputs,candidate,model)
            value=score(candidate,model)
            accepted=value>current
            trace.append(dict(round=iteration,operation=operation,before=current,proposal=value,
                              accepted=accepted,proposal_hash=canonical_hash(candidate)))
            if accepted: rows,current=candidate,value
    return rows,trace
