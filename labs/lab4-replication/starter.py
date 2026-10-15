"""Lab 4 starter: replicate Card & Krueger (1994), Table 4.

Usage: python starter.py data/public.dat

You are not expected to write this alone. Work with your AI assistant, but make
every modelling choice yourself and record it in your research log
(templates/research-log.md). The codebook and check.sas are in data/.
"""
import sys

import numpy as np
import pandas as pd

# Published Table 4, column (i)-(v): coefficient and standard error.
PUBLISHED = {
    "i": (2.33, 1.19),
    "ii": (2.30, 1.20),
    "iii": (15.65, 6.08),
    "iv": (14.92, 6.21),
    "v": (11.91, 7.39),
}

# TODO 1. Read public.dat. Which columns does the codebook describe, and how are
#         missing values coded?
df = pd.read_csv(sys.argv[1], sep=r"\s+", header=None, na_values=".")

# TODO 2. Build full-time-equivalent employment before and after (emptot, emptot2).
#         How are part-time workers and managers counted? Where does the paper say so?

# TODO 3. Treat closures. What happens to stores that closed permanently, and to
#         stores that were temporarily closed? Are they zero or missing?

# TODO 4. Define the regression sample. check.sas applies an extra restriction.
#         How many restaurants are left, and why?

# TODO 5. Estimate models (i)-(v) by OLS with conventional standard errors.
#         Compare the controls in check.sas with the footnotes under Table 4.


def ols(y, X):
    """OLS with conventional standard errors. X must include a constant."""
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    sigma2 = resid @ resid / (len(y) - X.shape[1])
    se = np.sqrt(np.diag(sigma2 * np.linalg.inv(X.T @ X)))
    return beta, se


# TODO 6. Compare each estimate with PUBLISHED and explain every difference.
#         Then pick one sensitivity check and report what changes.
