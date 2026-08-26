#!/usr/bin/env python3
"""Omnibenchmark module: guide_assignment_fishash.

Fishash guide assignment (one-sided Fisher exact + GS-FDR + Simpson refit).
Re-orchestration only: the vendored R script `scripts/run_fishash.R` is called
UNCHANGED via Rscript (the assignment_fishash env provides r-base + fishash +
Matrix). The injected MEX trio is presented as merged_{matrix,barcodes,features}
and read directly in R. Deterministic (no RNG).

Omnibenchmark CLI contract:
    --output_dir <dir> --name <node_id>
    --data.matrix / --data.barcodes / --data.features
    [--padj_cutoff <float>] [--padj_method <str>] [--min_count <int>] [--refit <int>]

Output: <output_dir>/assignments.csv   (cell,gRNA,UMI_counts,log_pval,odds_ratio_regularized)
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, "scripts")


def _mex_dir(matrix, barcodes, features, workdir):
    d = os.path.join(workdir, "mex")
    os.makedirs(d, exist_ok=True)
    for src, name in ((matrix, "merged_matrix.mtx.gz"),
                      (barcodes, "merged_barcodes.tsv.gz"),
                      (features, "merged_features.tsv.gz")):
        dst = os.path.join(d, name)
        if os.path.lexists(dst):
            os.remove(dst)
        os.symlink(os.path.abspath(src), dst)
    return d


def main():
    p = argparse.ArgumentParser(description="Omnibenchmark module: guide_assignment_fishash")
    p.add_argument("--output_dir", required=True)
    p.add_argument("--name", default="fishash")
    p.add_argument("--data.matrix", required=True)
    p.add_argument("--data.barcodes", required=True)
    p.add_argument("--data.features", required=True)
    p.add_argument("--padj_cutoff", default="0.05")
    p.add_argument("--padj_method", default="GS")
    p.add_argument("--min_count", default="2")
    p.add_argument("--refit", default="10")
    args = p.parse_args()

    matrix = getattr(args, "data.matrix")
    barcodes = getattr(args, "data.barcodes")
    features = getattr(args, "data.features")
    out = os.path.abspath(args.output_dir)
    os.makedirs(out, exist_ok=True)
    out_csv = os.path.join(out, "assignments.csv")

    with tempfile.TemporaryDirectory() as work:
        mex = _mex_dir(matrix, barcodes, features, work)
        rout = os.path.join(work, "fishash_out")
        cmd = ["Rscript", os.path.join(SCRIPTS, "run_fishash.R"),
               "--mex-dir", mex, "--output", rout,
               "--padj-cutoff", str(args.padj_cutoff),
               "--padj-method", str(args.padj_method),
               "--min-count", str(args.min_count),
               "--refit", str(args.refit)]
        print("+ " + " ".join(cmd), flush=True)
        subprocess.run(cmd, check=True)

        produced = os.path.join(rout, "assignments.csv")
        if not os.path.exists(produced):
            sys.exit(f"ERROR: fishash did not produce {produced}")
        shutil.copyfile(produced, out_csv)

    print("guide_assignment_fishash: wrote assignments.csv")


if __name__ == "__main__":
    main()
