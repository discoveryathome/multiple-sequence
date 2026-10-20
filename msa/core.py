"""MSA-SP-v1. Integer arithmetic; no external packages."""
from pathlib import Path
from itertools import combinations
import hashlib

ROOT = Path(__file__).resolve().parents[1]


def read_fasta(path):
    rows = {}
    name = None
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith('>'):
            name = line[1:].split()[0] if line[1:].split() else ''
            if not name or name in rows:
                raise ValueError('empty or duplicate sequence ID')
            rows[name] = ''
        else:
            if name is None or any(c.isspace() for c in line):
                raise ValueError('malformed FASTA')
            rows[name] += line.upper()
    if not rows or any(not s for s in rows.values()):
        raise ValueError('empty FASTA or sequence')
    return rows


def write_fasta(path, rows):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(''.join('>'+k+'\n'+rows[k]+'\n' for k in sorted(rows)))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_hash(rows):
    return hashlib.sha256(''.join('>'+k+'\n'+rows[k]+'\n' for k in sorted(rows)).encode()).hexdigest()


def matrix(model='protein'):
    if model == 'dna':
        return {(a,b): 2 if a == b else -1 for a in 'ACGT' for b in 'ACGT'}, 5, 1
    if model != 'protein':
        raise ValueError('unknown model')
    lines = [s.split() for s in (ROOT/'data/matrices/BLOSUM62').read_text().splitlines()
             if s.strip() and not s.startswith('#')]
    return {(r[0], c): int(x) for r in lines[1:] for c,x in zip(lines[0],r[1:]) if '*' not in (r[0],c)}, 11, 1


def validate(inputs, rows, model='protein'):
    if len(inputs) < 2 or set(inputs) != set(rows):
        raise ValueError('IDs differ or fewer than two sequences')
    alphabet = set('ACGT' if model == 'dna' else 'ARNDCQEGHILKMFPSTWYVBZX')
    if any(not s or set(s) - alphabet for s in inputs.values()):
        raise ValueError('invalid unaligned input alphabet')
    lengths = {len(s) for s in rows.values()}
    if len(lengths) != 1 or not next(iter(lengths)):
        raise ValueError('alignment must be nonempty and rectangular')
    for k in inputs:
        if set(rows[k]) - (alphabet | {'-'}) or rows[k].replace('-','') != inputs[k]:
            raise ValueError('residue mutation, loss, duplication, reorder, or invalid symbol: '+k)
    if any(all(c == '-' for c in col) for col in zip(*rows.values())):
        raise ValueError('all-gap column')
    return True


def strip_empty(rows):
    if not rows:
        return rows
    cols = [i for i,c in enumerate(zip(*rows.values())) if any(x != '-' for x in c)]
    return {k: ''.join(s[i] for i in cols) for k,s in rows.items()}


def pair_score(a,b,sub,op,ext):
    total, state = 0, 0
    for x,y in zip(a,b):
        if x == '-' and y == '-':
            continue  # Delete double gaps BEFORE identifying pairwise runs.
        if x == '-' or y == '-':
            side = 1 if x == '-' else 2
            total -= ext if side == state else op
            state = side
        else:
            total += sub[x,y]
            state = 0
    return total


def score(rows, model='protein'):
    sub,op,ext = matrix(model)
    return sum(pair_score(rows[a],rows[b],sub,op,ext) for a,b in combinations(sorted(rows),2))


def oracle_score(rows, model='protein'):
    """Independent run-length implementation, used only for verification."""
    sub,op,ext = matrix(model)
    value = 0
    for a,b in combinations(sorted(rows),2):
        pairs = [(x,y) for x,y in zip(rows[a],rows[b]) if (x,y) != ('-','-')]
        j = 0
        while j < len(pairs):
            x,y = pairs[j]
            if x != '-' and y != '-':
                value += sub[x,y]
                j += 1
            else:
                gap_index = 0 if x == '-' else 1
                end = j+1
                while end < len(pairs) and pairs[end][gap_index] == '-':
                    end += 1
                value -= op + (end-j-1)*ext
                j = end
    return value


def positions(rows):
    ids = sorted(rows)
    p = [0]*len(ids)
    cols = []
    for col in zip(*(rows[k] for k in ids)):
        out = []
        for i,c in enumerate(col):
            if c == '-':
                out.append(None)
            else:
                p[i] += 1
                out.append(p[i])
        cols.append(tuple(out))
    return cols


def accuracy(rows, reference, core):
    """Reference-pair recall and strict core-column recovery, with exact counts.

    Candidate pairs must be compared to ALL candidate columns, not candidate
    columns at the reference's numerical offsets. Residues use 1-based indices.
    Precision is restricted to pairs with both residues in the reference core.
    """
    if len(core) != len(next(iter(reference.values()))) or not any(core):
        raise ValueError('invalid/empty core mask')
    inputs = {k:s.replace('-','') for k,s in reference.items()}
    validate(inputs, rows)
    rc = [c for c,on in zip(positions(reference),core) if on]
    tc = positions(rows)
    def pairs(cols):
        return {(i,c[i],j,c[j]) for c in cols for i,j in combinations(range(len(c)),2)
                if c[i] is not None and c[j] is not None}
    rp = pairs(rc)
    tp = pairs(tc)
    residues = {(i,x) for c in rc for i,x in enumerate(c) if x is not None}
    restricted = {p for p in tp if (p[0],p[1]) in residues and (p[2],p[3]) in residues}
    hit = len(rp & tp)
    recovered = sum(c in set(tc) for c in rc)
    return dict(pair_hits=hit,reference_pairs=len(rp),candidate_core_pairs=len(restricted),
                core_columns=len(rc),column_hits=recovered,
                core_pair_recall=hit/len(rp) if rp else None,
                core_pair_precision=hit/len(restricted) if restricted else None,
                core_column_recall=recovered/len(rc))
