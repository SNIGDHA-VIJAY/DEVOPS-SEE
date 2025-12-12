#!/usr/bin/env python3
import argparse, csv, glob, json, os, sys

def parse_args():
    p = argparse.ArgumentParser(description="CSV column consistency + required columns check")
    p.add_argument("--csv-glob", required=True, help="Glob for CSV files, e.g. data/*.csv")
    p.add_argument("--required-cols", required=True, help="Comma-separated required columns")
    p.add_argument("--out", default="report/data_quality_summary.json", help="JSON report path")
    return p.parse_args()

def read_header(path):
    with open(path, newline="", encoding="utf-8") as f:
        rdr = csv.reader(f)
        try:
            return next(rdr)
        except StopIteration:
            return []  # empty file

def main():
    args = parse_args()
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    files = sorted(glob.glob(args.csv_glob))
    required = [c.strip() for c in args.required_cols.split(",") if c.strip()]

    summary = {
        "checked_files": files,
        "required_columns": required,
        "per_file": [],
        "missing_columns_detected": False,
        "inconsistent_headers_detected": False,
        "reference_header": None
    }

    ref_header = None
    for fp in files:
        hdr = read_header(fp)
        if ref_header is None:
            ref_header = hdr
            summary["reference_header"] = ref_header

        missing = [c for c in required if c not in hdr]
        if hdr != ref_header:
            summary["inconsistent_headers_detected"] = True

        summary["per_file"].append({
            "file": fp,
            "header": hdr,
            "missing_required_columns": missing,
            "missing_count": len(missing)
        })

        if missing:
            summary["missing_columns_detected"] = True

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # Exit non-zero if missing required columns are found
    if summary["missing_columns_detected"]:
        print("ERROR: Missing required columns detected. See JSON summary.")
        sys.exit(1)

    # You can choose to fail or not on inconsistent headers. Here we only warn:
    if summary["inconsistent_headers_detected"]:
        print("WARNING: Inconsistent headers across files (build will still pass).")

if __name__ == "__main__":
    main()
