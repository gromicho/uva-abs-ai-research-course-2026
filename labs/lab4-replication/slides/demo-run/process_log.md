# Process log: replicating Card & Krueger (1994) Table 4

## Step 1 - Download
- `curl -sSL` both URLs into the project folder. Both exit code 0.
  `file` reports: PDF 1.4, 27 pages (595,695 bytes); zip archive (23,017 bytes).
- No errors.

## Step 2 - Unzip
- Unzipped into subfolder `njmin/` (kept separate from my own script).
  Files: check.sas, codebook, public.dat, read.me, survey1.nj, survey2.nj.
- public.dat: 410 lines, every line has 46 whitespace-separated fields, `.` = missing
  (matches the 46 variables in the SAS `INPUT` list).

## Step 3 - Read Table 4
- Did not try fetching the PDF as a web page; read the saved PDF directly with the
  Read tool, page 10 (rendered image of the scanned page; journal page 780).
- Values read off the rendered image:
  - (i)  NJ dummy 2.33 (1.19); SER 8.79
  - (ii) NJ dummy 2.30 (1.20); chain/ownership controls; SER 8.78; p(controls)=0.34
  - (iii) gap 15.65 (6.08); SER 8.76
  - (iv) gap 14.92 (6.21); chain/ownership; SER 8.76; p=0.44
  - (v)  gap 11.91 (7.39); chain/ownership + region; SER 8.75; p=0.40
  - Notes: sample = 357 stores; dep. var mean -0.237, s.d. 8.825.
- Observation: check.sas orders the models differently (gap models first, then NJ),
  and its third DEMP model is `GAP BK KFC ROYS CENTRALJ SOUTHJ PA1 PA2` - it OMITS
  CO_OWNED, although the paper's note b says column (v) includes ownership.
  (The PCHEMPC version of the same model in check.sas does include CO_OWNED.)
  Plan: translate check.sas literally, and also run the variant with CO_OWNED,
  and report both against the paper.

## Step 4 - Translate check.sas to Python (replicate_table4.py)
- Read public.dat with `pd.read_csv(sep=r"\s+", na_values=["."])`, 46 column names
  taken from the SAS INPUT statement (CHAINr/STATEr kept as chainr/stater).
- Derived EMPTOT, EMPTOT2, DEMP, PCHEMPC, DWAGE, GAP, NJ, chain dummies, CLOSED
  exactly as in the SAS DATA step (NaN propagation mimics SAS missing; GAP's
  else-branch gives missing when NJ wage_st is missing).
- DATA C1 filter: DEMP not missing AND (CLOSED=1 OR (CLOSED=0 AND DWAGE not missing)).
- PROC REG translated to NumPy OLS (lstsq) with classical SEs, root MSE (SER), and a
  joint F test of all controls (restricted = key regressor + constant). Regularized
  incomplete beta coded by hand so only pandas/NumPy are used (scipy exists on the
  machine but I did not use it).
- Mimicked PROC REG's rule that one common sample is used for all MODEL statements
  in one PROC (listwise deletion over all model variables); it turned out to drop
  nobody (C1 = 357 already).
- Considered and checked: no run errors on the first execution of the script.

## Step 5 - First run, compare to paper
- N = 357 (paper: 357). DEMP mean -0.2375 (prints -0.238; paper says -0.237 -
  a rounding difference in the 3rd decimal), s.d. 8.825 (paper 8.825).
- Columns (i)-(iv): coefficient, SE, SER and p-value all match the paper to 2 decimals.
- MISMATCH in column (v) with the literal check.sas model (no CO_OWNED):
  coef 11.91 and SE 7.39 match the paper, but SER 8.74 (paper 8.75) and
  p(controls) 0.31 (paper 0.40) do not.
- Tried the variant with CO_OWNED added (as the paper's note b describes):
  SER 8.75 and p = 0.40 now match, but coef becomes 11.98 (7.42) instead of 11.91 (7.39).
- Conclusion (not fixed, just reported): the published column (v) appears to mix
  the two specifications - the coefficient/SE come from the check.sas model without
  CO_OWNED, while the SER and F-test p-value match the model with CO_OWNED. I can't
  tell from the files which one the authors intended; script prints both.

## Step 6 - Follow-up: which stores were left out
- 410 stores total, 357 used, 53 left out:
  - 26 with DEMP missing (FTE missing in wave 1: 12; in wave 2: 14). Of these,
    4 were temporarily closed in wave 2 (status2 = 2 renovations x2, 4 highway, 5 mall fire)
    and 1 refused the 2nd interview (status2 = 0); the other 21 answered but had
    missing employment items.
  - 27 open stores with FTE data but a missing starting wage in wave 1 (19) or
    wave 2 (9) (one store, sheet 255, missing both): 19 NJ, 8 PA.
- The 6 permanently closed stores (status2 = 3) are KEPT, with wave-2 FTE = 0,
  even if wages are missing (they are exempt from the wage condition).
- Final run output saved to table4_output.txt via shell redirect.
