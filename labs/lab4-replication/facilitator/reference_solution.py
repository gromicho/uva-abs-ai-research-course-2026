"""Independent replication of Card & Krueger (1994), Tables 3 and 4, plus robustness checks.

Usage: python -I ck_replicate.py <path/to/public.dat>
Translates check.sas (Card's released program) line by line; OLS via numpy.
Exits non-zero if any published Table 4 coefficient or SE fails to match at 2 decimals.
"""
import sys
import time

import numpy as np
import pandas as pd

t0 = time.perf_counter()

COLS = """sheet chain co_owned state southj centralj northj pa1 pa2 shore ncalls empft emppt
nmgrs wage_st inctime firstinc bonus pctaff meals open hrsopen psoda pfry pentree nregs nregs11
type2 status2 date2 ncalls2 empft2 emppt2 nmgrs2 wage_st2 inctime2 firstin2 special2 meals2
open2r hrsopen2 psoda2 pfry2 pentree2 nregs2 nregs112""".split()

df = pd.read_csv(sys.argv[1], sep=r"\s+", header=None, names=COLS, na_values=".")
assert len(df) == 410 and df.shape[1] == 46, df.shape


def build(d, pt_weight=0.5):
    d = d.copy()
    d["emptot"] = d.emppt * pt_weight + d.empft + d.nmgrs
    d["emptot2"] = d.emppt2 * pt_weight + d.empft2 + d.nmgrs2
    d["demp"] = d.emptot2 - d.emptot
    d["pchempc"] = 2 * d.demp / (d.emptot2 + d.emptot)
    d.loc[d.emptot2 == 0, "pchempc"] = -1
    d["dwage"] = d.wage_st2 - d.wage_st
    gap = np.where(d.wage_st >= 5.05, 0.0, (5.05 - d.wage_st) / d.wage_st)
    gap = np.where(d.wage_st.isna(), np.nan, gap)
    d["gap"] = np.where(d.state == 0, 0.0, gap)
    d["nj"] = d.state
    for k, name in enumerate(["bk", "kfc", "roys", "wendys"], 1):
        d[name] = (d.chain == k).astype(float)
    d["closed"] = (d.status2 == 3).astype(float)
    return d


def ols(d, y, xs, se="conv"):
    d = d[[y] + xs].dropna()
    X = np.column_stack([np.ones(len(d))] + [d[x].to_numpy(float) for x in xs])
    Y = d[y].to_numpy(float)
    XtXi = np.linalg.inv(X.T @ X)
    b = XtXi @ X.T @ Y
    e = Y - X @ b
    n, k = X.shape
    if se == "conv":
        V = XtXi * (e @ e) / (n - k)
    else:  # HC1
        V = XtXi @ (X.T * e**2) @ X @ XtXi * n / (n - k)
    return b[1], np.sqrt(V[1, 1]), n, np.sqrt(e @ e / (n - k))


d = build(df)
# SAS: IF DEMP NE . ; IF CLOSED=1 OR (CLOSED=0 AND DWAGE NE .);
c1 = d[d.demp.notna() & ((d.closed == 1) | ((d.closed == 0) & d.dwage.notna()))]
emp_sample = d[d.demp.notna()]

CH = ["bk", "kfc", "roys", "co_owned"]
REG = ["centralj", "southj", "pa1", "pa2"]
SPECS = {
    "(i)   NJ": ["nj"],
    "(ii)  NJ + chain/own": ["nj"] + CH,
    "(iii) GAP": ["gap"],
    "(iv)  GAP + chain/own": ["gap"] + CH,
    "(v)   GAP + chain + region [SAS: no co_owned]": ["gap", "bk", "kfc", "roys"] + REG,
}
PUBLISHED = {"(i)   NJ": (2.33, 1.19), "(ii)  NJ + chain/own": (2.30, 1.20),
             "(iii) GAP": (15.65, 6.08), "(iv)  GAP + chain/own": (14.92, 6.21),
             "(v)   GAP + chain + region [SAS: no co_owned]": (11.91, 7.39)}

lines = []
out = lines.append
out(f"Rows read: {len(df)}; employment-change sample: {len(emp_sample)}; Table 4 sample (c1): {len(c1)}")
out(f"Table 4 note check: mean demp {c1.demp.mean():.3f}, sd {c1.demp.std():.3f}  (published -0.237, 8.825)")

out("\nTable 3 (FTE, part-time = 0.5)")
for s, lab in [(0, "PA"), (1, "NJ")]:
    g = d[d.state == s]
    bal = g[g.demp.notna()]
    out(f"  {lab}: before {g.emptot.mean():.2f} (n={g.emptot.notna().sum()}), after {g.emptot2.mean():.2f} "
        f"(n={g.emptot2.notna().sum()}), balanced change {bal.demp.mean():.2f} (n={len(bal)})")
did_bal = ols(emp_sample, "demp", ["nj"])
out(f"  Balanced-sample DiD (row 4): {did_bal[0]:.2f} ({did_bal[1]:.2f}), n={did_bal[2]}")

out("\nTable 4 (conventional SEs; sample n=357)")
fails = 0
for name, xs in SPECS.items():
    b, s, n, ser = ols(c1, "demp", xs)
    pb, ps = PUBLISHED[name]
    ok = round(b, 2) == pb and round(s, 2) == ps
    fails += not ok
    out(f"  {name:48s} {b:7.2f} ({s:.2f})  n={n}  SER={ser:.2f}  published {pb} ({ps})  {'MATCH' if ok else 'MISMATCH'}")

out("\nSensitivity analysis")
b, s, n, _ = ols(c1, "demp", ["gap", "bk", "kfc", "roys", "co_owned"] + REG)
out(f"  (v) with co_owned as footnote b implies:          {b:.2f} ({s:.2f}) n={n}")
for name, xs in SPECS.items():
    b, s, n, _ = ols(c1, "demp", xs, se="hc1")
    out(f"  HC1 robust SE {name:40s} {b:.2f} ({s:.2f})")
for w in (0.0, 0.4, 0.5, 0.6, 1.0):
    dw = build(df, w)
    cw = dw[dw.demp.notna() & ((dw.closed == 1) | ((dw.closed == 0) & dw.dwage.notna()))]
    b1, s1, _, _ = ols(cw, "demp", ["nj"])
    b3, s3, _, _ = ols(cw, "demp", ["gap"])
    out(f"  part-time weight {w:.1f}: NJ {b1:.2f} ({s1:.2f}), GAP {b3:.2f} ({s3:.2f})")
no_closed = c1[c1.closed == 0]
b, s, n, _ = ols(no_closed, "demp", ["nj"])
out(f"  drop 6 permanently closed stores: NJ {b:.2f} ({s:.2f}) n={n}")
temp = d.copy()
temp_closed = temp.status2.isin([2, 4, 5])
temp.loc[temp_closed, ["emptot2"]] = 0
temp["demp"] = temp.emptot2 - temp.emptot
b, s, n, _ = ols(temp[temp.demp.notna()], "demp", ["nj"])
out(f"  Table 3 row 5 (temp. closed set to 0): NJ {b:.2f} ({s:.2f}) n={n}")
for name, xs in [("NJ", ["nj"]), ("GAP", ["gap"])]:
    b, s, n, _ = ols(c1, "pchempc", xs)
    out(f"  proportional change, {name}: {b:.3f} ({s:.3f}) n={n}")

# Who is dropped going from 384 to 357?
dropped = emp_sample.loc[~emp_sample.index.isin(c1.index)]
out(f"\n  Dropped from employment sample by wage restriction: {len(dropped)} "
    f"(NJ {int(dropped.nj.sum())}, PA {int((dropped.nj == 0).sum())}); "
    f"missing wage_st {int(dropped.wage_st.isna().sum())}, missing wage_st2 {int(dropped.wage_st2.isna().sum())}; "
    f"mean demp {dropped.demp.mean():.2f}")

out(f"\nElapsed analysis time: {time.perf_counter() - t0:.2f} s")
print("\n".join(lines))
if fails:
    print(f"FAIL: {fails} Table 4 entries do not match", file=sys.stderr)
    sys.exit(1)
print("ALL 5 TABLE 4 ENTRIES MATCH")
