"""Translate check.sas (Card & Krueger 1994, NJ-PA minimum wage data) into
pandas/NumPy and reproduce Table 4 (reduced-form models for change in FTE
employment).

Usage:  python -I replicate_table4.py [path/to/public.dat]
"""
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "njmin" / "public.dat"

# ---- DATA CHECK; INFILE IN; INPUT ... (SAS list input, '.' = missing) ----
COLS = """SHEET CHAINR CO_OWNED STATER SOUTHJ CENTRALJ NORTHJ PA1 PA2 SHORE NCALLS
EMPFT EMPPT NMGRS WAGE_ST INCTIME FIRSTINC BONUS PCTAFF MEAL OPEN HRSOPEN PSODA
PFRY PENTREE NREGS NREGS11 TYPE2 STATUS2 DATE2 NCALLS2 EMPFT2 EMPPT2 NMGRS2
WAGE_ST2 INCTIME2 FIRSTIN2 SPECIAL2 MEALS2 OPEN2R HRSOPEN2 PSODA2 PFRY2 PENTREE2
NREGS2 NREGS112""".split()
assert len(COLS) == 46

df = pd.read_csv(DATA, sep=r"\s+", header=None, names=COLS, na_values=["."])
df.columns = [c.lower() for c in df.columns]
d = df

# ---- derived variables (NaN propagates like SAS missing) ----
d["emptot"] = d.emppt * 0.5 + d.empft + d.nmgrs
d["emptot2"] = d.emppt2 * 0.5 + d.empft2 + d.nmgrs2
d["demp"] = d.emptot2 - d.emptot

d["pchempc"] = 2 * (d.emptot2 - d.emptot) / (d.emptot2 + d.emptot)
d.loc[d.emptot2 == 0, "pchempc"] = -1

d["dwage"] = d.wage_st2 - d.wage_st
d["pchwage"] = (d.wage_st2 - d.wage_st) / d.wage_st

# if stater=0 then gap=0; else if wage_st>=5.05 then gap=0;
# else if wage_st>0 then gap=(5.05-wage_st)/wage_st; else gap=.;
# (SAS: missing wage_st compares as smaller than any number -> gap=.)
gap = np.full(len(d), np.nan)
pa = d.stater == 0
hi = ~pa & (d.wage_st >= 5.05)
lo = ~pa & ~hi & (d.wage_st > 0)
gap[pa | hi] = 0.0
gap[lo] = ((5.05 - d.wage_st) / d.wage_st)[lo]
d["gap"] = gap

d["nj"] = d.stater
d["bk"] = (d.chainr == 1).astype(float)
d["kfc"] = (d.chainr == 2).astype(float)
d["roys"] = (d.chainr == 3).astype(float)
d["wendys"] = (d.chainr == 4).astype(float)
d["closed"] = (d.status2 == 3).astype(float)

# ---- DATA C1: IF DEMP NE .; IF CLOSED=1 OR (CLOSED=0 AND DWAGE NE .); ----
c1 = d[d.demp.notna()]
c1 = c1[(c1.closed == 1) | ((c1.closed == 0) & c1.dwage.notna())]

# ---- PROC REG S;  (the 5 DEMP models, in check.sas order) ----
SAS_MODELS = {
    "gap":                ["gap"],
    "gap+chain":          ["gap", "bk", "kfc", "roys", "co_owned"],
    "gap+chain+region":   ["gap", "bk", "kfc", "roys", "centralj", "southj", "pa1", "pa2"],
    "nj":                 ["nj"],
    "nj+chain":           ["nj", "bk", "kfc", "roys", "co_owned"],
}
# Variant: column (v) as the paper's notes describe it (chain AND ownership + region)
VARIANT = ["gap", "bk", "kfc", "roys", "co_owned", "centralj", "southj", "pa1", "pa2"]

# PROC REG with several MODEL statements drops an observation if ANY variable
# used in ANY of its MODEL statements is missing -> one common sample.
used = sorted({v for xs in SAS_MODELS.values() for v in xs} | {"demp"})
sample = c1.dropna(subset=used)


def betainc_reg(a, b, x):
    """Regularized incomplete beta I_x(a,b) (continued fraction, Numerical Recipes)."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    front = math.exp(lbeta + a * math.log(x) + b * math.log(1 - x))
    if x > (a + 1) / (a + b + 2):
        return 1.0 - betainc_reg(b, a, 1 - x)
    f, c, dd = 1.0, 1.0, 0.0
    for i in range(400):
        m = i // 2
        if i == 0:
            num = 1.0
        elif i % 2 == 0:
            num = m * (b - m) * x / ((a + 2 * m - 1) * (a + 2 * m))
        else:
            num = -(a + m) * (a + b + m) * x / ((a + 2 * m) * (a + 2 * m + 1))
        dd = 1.0 + num * dd
        dd = 1.0 / (dd if abs(dd) > 1e-300 else 1e-300)
        c = 1.0 + num / c
        c = c if abs(c) > 1e-300 else 1e-300
        f *= c * dd
        if abs(1.0 - c * dd) < 1e-14:
            break
    return front * (f - 1.0) / a


def f_pvalue(F, q, dfd):
    return 1.0 - betainc_reg(q / 2.0, dfd / 2.0, q * F / (q * F + dfd))


def ols(data, xs, y="demp"):
    Y = data[y].to_numpy(float)
    X = np.column_stack([np.ones(len(data))] + [data[v].to_numpy(float) for v in xs])
    n, k = X.shape
    beta, *_ = np.linalg.lstsq(X, Y, rcond=None)
    resid = Y - X @ beta
    ssr = float(resid @ resid)
    s2 = ssr / (n - k)
    se = np.sqrt(np.diag(s2 * np.linalg.inv(X.T @ X)))
    return dict(n=n, k=k, beta=beta[1:], se=se[1:], ser=math.sqrt(s2), ssr=ssr, xs=xs)


def control_p(data, full, key):
    """p-value of joint F test excluding all controls (everything except key)."""
    u = ols(data, full)
    r = ols(data, [key])
    q = len(full) - 1
    F = ((r["ssr"] - u["ssr"]) / q) / (u["ssr"] / (u["n"] - u["k"]))
    return f_pvalue(F, q, u["n"] - u["k"])


res = {name: ols(sample, xs) for name, xs in SAS_MODELS.items()}
res_var = ols(sample, VARIANT)

# Paper Table 4 (read from rendered PDF page 10): column -> (key, coef, se, SER, p)
PAPER = [
    ("(i)",   "nj",               "nj",  2.33, 1.19, 8.79, None),
    ("(ii)",  "nj+chain",         "nj",  2.30, 1.20, 8.78, 0.34),
    ("(iii)", "gap",              "gap", 15.65, 6.08, 8.76, None),
    ("(iv)",  "gap+chain",        "gap", 14.92, 6.21, 8.76, 0.44),
    ("(v)",   "gap+chain+region", "gap", 11.91, 7.39, 8.75, 0.40),
]

lines = []
p = lines.append
p("Card & Krueger (1994) Table 4 - replication of check.sas in pandas/NumPy")
p(f"Stores in public.dat: {len(d)}; in DATA C1 subset: {len(c1)}; "
  f"used in PROC REG (no missing in any model var): {len(sample)}  [paper: 357]")
p(f"Dependent variable DEMP: mean {sample.demp.mean():.3f}, s.d. {sample.demp.std(ddof=1):.3f}"
  f"  [paper: -0.237, 8.825]")
p("")
hdr = f"{'Col':6}{'Regressor':10}{'Coef':>9}{'Paper':>8}{'SE':>8}{'Paper':>8}{'SER':>7}{'Paper':>7}{'p(ctrl)':>9}{'Paper':>7}"
p(hdr)
p("-" * len(hdr))
for col, name, key, pc, pse, pser, pp in PAPER:
    r = res[name]
    i = r["xs"].index(key)
    ptxt = f"{control_p(sample, r['xs'], key):.2f}" if len(r["xs"]) > 1 else "-"
    pptxt = f"{pp:.2f}" if pp is not None else "-"
    p(f"{col:6}{key.upper():10}{r['beta'][i]:9.2f}{pc:8.2f}{r['se'][i]:8.2f}{pse:8.2f}"
      f"{r['ser']:7.2f}{pser:7.2f}{ptxt:>9}{pptxt:>7}")
p("")
p("Column (v) in check.sas omits CO_OWNED (MODEL DEMP=GAP BK KFC ROYS CENTRALJ SOUTHJ PA1 PA2).")
p("Variant with CO_OWNED added, as the paper's note b describes column (v):")
i = VARIANT.index("gap")
p(f"{'(v)*':6}{'GAP':10}{res_var['beta'][i]:9.2f}{11.91:8.2f}{res_var['se'][i]:8.2f}{7.39:8.2f}"
  f"{res_var['ser']:7.2f}{8.75:7.2f}{control_p(sample, VARIANT, 'gap'):9.2f}{0.40:7.2f}")
p("")
p("Full coefficient listing (check.sas models):")
for name, r in res.items():
    terms = ", ".join(f"{v}={b:.3f} ({s:.3f})" for v, b, s in zip(r["xs"], r["beta"], r["se"]))
    p(f"  DEMP ~ {name:18} n={r['n']}: {terms}")

# ---- Who was left out? ----
p("")
p("Stores left out of the regressions:")
no_demp = d[d.demp.isna()]
p(f"  DEMP missing (FTE employment missing in wave 1 and/or wave 2): {len(no_demp)}")
p(f"    of which: wave-1 FTE missing {int(no_demp.emptot.isna().sum())}, "
  f"wave-2 FTE missing {int(no_demp.emptot2.isna().sum())}, "
  f"both missing {int((no_demp.emptot.isna() & no_demp.emptot2.isna()).sum())}")
p(f"    status2 of these: {no_demp.status2.value_counts().sort_index().to_dict()}")
have = d[d.demp.notna()]
drop_w = have[~((have.closed == 1) | ((have.closed == 0) & have.dwage.notna()))]
p(f"  DEMP present but open store with missing wage in wave 1 or 2 (DWAGE missing): {len(drop_w)}")
p(f"    wave-1 wage missing {int(drop_w.wage_st.isna().sum())}, "
  f"wave-2 wage missing {int(drop_w.wage_st2.isna().sum())}; "
  f"NJ {int((drop_w.nj == 1).sum())}, PA {int((drop_w.nj == 0).sum())}")
drop_m = c1[~c1.index.isin(sample.index)]
p(f"  In C1 but missing a model variable (e.g. GAP for closed store w/o wave-1 wage): {len(drop_m)}")
if len(drop_m):
    p("    sheets: " + ", ".join(str(int(s)) for s in drop_m.sheet))
cl = d[d.closed == 1]
p(f"  Permanently closed stores (status2=3): {len(cl)}, kept in sample: "
  f"{int(cl.index.isin(sample.index).sum())} (wave-2 FTE = 0)")
p(f"  Total left out: {len(d) - len(sample)} of {len(d)}")

out = "\n".join(lines)
print(out)
