# ERRATA

## E-001: Percentage delta calculation (+19% vs 6.38%)

**Issue:** A narrative claim used a **simple difference** (+19%) where the underlying data supports a **compounded or normalized figure** (6.38%).

**Fix:** All percentage improvements must specify **method**:
- `Δ%` (absolute difference) vs `CAGR` vs `relative uplift`.
- Modified text to: "**+6.38% (CAGR)**" with footnote explaining baseline and window.

**Method Formulae:**
- Absolute difference: `(x1 - x0) / x0`
- CAGR for n periods: `(x_n / x_0)^(1/n) - 1`

**Action:** Added `tools/recalc_metrics.py` to scan docs for `%` claims and enforce footnote syntax `[^calc]` adjacent to any `%` value without bracketed method. The script exits non‑zero if violations exist (CI gate).
