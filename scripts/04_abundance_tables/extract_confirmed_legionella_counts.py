#!/usr/bin/env python3

import re
import csv
import argparse
from pathlib import Path

def parse_fasta_counts(fasta):
    sample = fasta.name.replace(".confirmed_legionella.fasta", "")
    rows = []

    with open(fasta) as f:
        for line in f:
            if line.startswith(">"):
                header = line[1:].strip()
                asv_id = header.split(";size=")[0].split()[0]

                match = re.search(r";size=(\d+);", header)
                count = int(match.group(1)) if match else 1

                rows.append((sample, asv_id, count))

    return rows

def main():
    parser = argparse.ArgumentParser(
        description="Extract confirmed Legionella ASV counts from FASTA size= headers."
    )
    parser.add_argument("--indir", required=True)
    parser.add_argument("--out", required=True)

    args = parser.parse_args()

    fasta_files = sorted(Path(args.indir).glob("*.confirmed_legionella.fasta"))

    with open(args.out, "w", newline="") as out:
        writer = csv.writer(out, delimiter="\t")
        writer.writerow(["sample", "asv_id", "count"])

        for fasta in fasta_files:
            for row in parse_fasta_counts(fasta):
                writer.writerow(row)

if __name__ == "__main__":
    main()