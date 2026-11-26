#!/usr/bin/env python3
"""Reference solver (instructors only). Usage: python3 solve.py <level> <file>"""
import base64, sys, string
from collections import Counter
U = string.ascii_uppercase
ENG = [8.2,1.5,2.8,4.3,12.7,2.2,2.0,6.1,7.0,.15,.77,4.0,2.4,6.7,7.5,1.9,.095,6.0,6.3,9.1,2.8,.98,2.4,.15,2.0,.074]

def chi(col):
    c = Counter(col); n = len(col)
    return min(range(26), key=lambda s: sum((c[U[(i+s)%26]]-n*ENG[i]/100)**2/(n*ENG[i]/100) for i in range(26)))

def ic(s):
    c = Counter(s); n = len(s)
    return sum(v*(v-1) for v in c.values())/(n*(n-1))

lvl, data = sys.argv[1], open(sys.argv[2]).read().strip()
if lvl == "0":
    print(base64.b64decode(data).decode())
elif lvl == "1":
    for s in range(1, 26):
        print(s, "".join(U[(U.index(c)-s)%26] if c in U else c for c in data))
elif lvl == "2":
    t = "".join(c for c in data if c in U)
    L = max(range(4, 11), key=lambda L: sum(ic(t[i::L]) for i in range(L))/L)
    key = "".join(U[chi(t[i::L])] for i in range(L))
    print("key:", key)
    print("".join(U[(U.index(c)-U.index(key[i%L]))%26] for i, c in enumerate(t)))
elif lvl == "3":
    ct = bytes.fromhex(data); kp = b"KRYPTON TRANSMISSION"
    ks = bytes(a ^ b for a, b in zip(ct, kp))
    L = next(l for l in range(1, len(ks)) if ks[l:] == ks[:len(ks)-l])
    print(bytes(b ^ ks[i % L] for i, b in enumerate(ct)).decode())
