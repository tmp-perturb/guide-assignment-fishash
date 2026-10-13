# guide-assignment-fishash

fishash (R) guide-assignment method module for the
[guide-assignment](https://github.com/yunzhe-liu/guide-assignment) Omnibenchmark.
One-sided Fisher exact test with GS-FDR and Simpson refit.

The two required runtime source files from `jackkamm/fishash` 0.99.0 are
vendored at upstream commit `74220e8`. This removes the former personal
R-library dependency and avoids downloading software during a benchmark run.
Provenance and upstream licenses are retained under `vendor/fishash/`.

- Entrypoint: `run.py` (wraps `Rscript`)  ·  Input: MEX trio  ·  Output: `assignments.csv`
