#!/usr/bin/env python3

import os
import csv
import argparse
from pathlib import Path

def read_fasta(fasta_path):
    records = {}
    header = None
    seq_lines = []

    with open(fasta_path) as f:
        for line in f:
            line = line.rstrip()
            if line.startswith(">"):
                if header is not None:
                    records[header.split()[0]] = (header, "".join(seq_lines))
                header = line[1:]
                seq_lines = []
            else:
                seq_lines.append(line)

        if header is not None:
            records[header.split()[0]] = (header, "".join(seq_lines))

    return records

def write_fasta(records, names, output_fasta):
    with open(output_fasta, "w") as out:
        for name in names:
            if name in records:
                header, seq = records[name]
                out.write(f">{header}\n{seq}\n")

def main():
    parser = argparse.ArgumentParser(
        description="Extract candidate Legionella hits from BLAST CSVs and matching FASTA records."
    )

    parser.add_argument("--blast_dir", required=True)
    parser.add_argument("--fasta_dir", required=True)
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--hit_prefix", default="f_leg_")

    args = parser.parse_args()

    blast_dir = Path(args.blast_dir)
    fasta_dir = Path(args.fasta_dir)
    outdir = Path(args.outdir)

    filtered_csv_dir = outdir / "filtered_csvs"
    names_dir = outdir / "sequence_names"
    fasta_out_dir = outdir / "candidate_legionella_fastas"

    filtered_csv_dir.mkdir(parents=True, exist_ok=True)
    names_dir.mkdir(parents=True, exist_ok=True)
    fasta_out_dir.mkdir(parents=True, exist_ok=True)

    for blast_csv in blast_dir.glob("*.csv"):
        sample = blast_csv.stem.replace("_blast", "")

        filtered_rows = []
        seq_names = []

        with open(blast_csv, newline="") as f:
            reader = csv.reader(f)

            for row in reader:
                if len(row) < 2:
                    continue

                query_id = row[0]
                subject_id = row[1]

                if subject_id.startswith(args.hit_prefix):
                    filtered_rows.append(row)
                    seq_names.append(query_id)

        filtered_csv = filtered_csv_dir / f"{sample}_legionella_hits.csv"
        names_file = names_dir / f"{sample}_legionella_sequence_names.txt"

        with open(filtered_csv, "w", newline="") as out:
            writer = csv.writer(out)
            writer.writerows(filtered_rows)

        with open(names_file, "w") as out:
            for name in seq_names:
                out.write(name + "\n")

        # assumes matching FASTA has same sample stem
        fasta_file = fasta_dir / f"{sample}.fasta"

        if fasta_file.exists():
            fasta_records = read_fasta(fasta_file)
            output_fasta = fasta_out_dir / f"{sample}_candidate_legionella.fasta"
            write_fasta(fasta_records, seq_names, output_fasta)
            print(f"{sample}: {len(seq_names)} hits extracted")
        else:
            print(f"WARNING: no matching FASTA found for {sample}: {fasta_file}")

if __name__ == "__main__":
    main()