#!/usr/bin/env python3

import os
import sys
import gzip
import hashlib
import argparse
from pathlib import Path


def open_maybe_gzip(path):
    if str(path).endswith((".gz", ".gzip")):
        return gzip.open(path, "rt")
    return open(path, "r")


def iter_fasta(path):
    """Yield (id, sequence) from FASTA. ID = header up to first whitespace."""
    with open_maybe_gzip(path) as fh:
        header = None
        seq_chunks = []

        for line in fh:
            line = line.rstrip("\n")

            if not line:
                continue

            if line.startswith(">"):
                if header is not None:
                    yield header, "".join(seq_chunks)

                header = line[1:].split()[0]
                seq_chunks = []
            else:
                seq_chunks.append(line.strip())

        if header is not None:
            yield header, "".join(seq_chunks)


def norm_seq(seq):
    """Normalize sequences before matching."""
    return seq.upper().replace("U", "T").replace("-", "").replace(" ", "")


_COMP = str.maketrans("ACGTRYKMSWBDHVN", "TGCAYRMKSWVHDBN")


def revcomp(seq):
    return seq.translate(_COMP)[::-1]


def sha1(seq):
    return hashlib.sha1(seq.encode("ascii", "ignore")).hexdigest()


def canonical_hash(seq, use_rc):
    """Hash sequence, optionally treating reverse complement as equivalent."""
    if not use_rc:
        return sha1(seq)

    rc = revcomp(seq)
    h1 = sha1(seq)
    h2 = sha1(rc)

    return h1 if h1 < h2 else h2


def build_ref_hashes(ref_fasta, use_rc):
    ref_hashes = set()
    n_records = 0

    for _id, seq in iter_fasta(ref_fasta):
        n_records += 1
        normalized = norm_seq(seq)

        if normalized:
            ref_hashes.add(canonical_hash(normalized, use_rc))

    return ref_hashes, n_records


def sample_name_from_path(path):
    stem = Path(path).name

    for ext in (".fasta", ".fa", ".fna", ".fas", ".gz"):
        if stem.endswith(ext):
            stem = stem[: -len(ext)]

    return stem


def wrap_seq(seq, width=80):
    return "\n".join(seq[i:i + width] for i in range(0, len(seq), width))


def process_one(sample_fasta, ref_hashes, outdir, use_rc):
    sample = sample_name_from_path(sample_fasta)
    out_path = Path(outdir) / f"{sample}.confirmed_legionella.fasta"

    os.makedirs(outdir, exist_ok=True)

    total = 0
    hits = 0
    seen_ids = set()

    with open(out_path, "w") as out:
        for record_id, seq in iter_fasta(sample_fasta):
            total += 1
            normalized = norm_seq(seq)

            if not normalized:
                continue

            if canonical_hash(normalized, use_rc) in ref_hashes:
                if record_id not in seen_ids:
                    out.write(f">{record_id}\n{wrap_seq(seq)}\n")
                    seen_ids.add(record_id)
                    hits += 1

    return sample, total, hits, str(out_path)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Extract per-sample FASTA records whose sequences exactly match a "
            "phylogenetically confirmed Legionella ASV reference FASTA."
        )
    )

    parser.add_argument(
        "--ref",
        required=True,
        help="Confirmed Legionella ASV FASTA reference."
    )

    parser.add_argument(
        "--inputs",
        nargs="+",
        help="One or more per-sample candidate FASTA files."
    )

    parser.add_argument(
        "--list",
        help="Text file with one per-sample candidate FASTA path per line."
    )

    parser.add_argument(
        "--outdir",
        default="confirmed_legionella_fastas",
        help="Output directory."
    )

    parser.add_argument(
        "--rc",
        action="store_true",
        help="Treat reverse complements as matching sequences."
    )

    args = parser.parse_args()

    sample_paths = []

    if args.inputs:
        sample_paths.extend(args.inputs)

    if args.list:
        with open(args.list) as f:
            for line in f:
                line = line.strip()

                if line and not line.startswith("#"):
                    sample_paths.append(line)

    if not sample_paths:
        print("No input FASTA files provided. Use --inputs or --list.", file=sys.stderr)
        sys.exit(2)

    print(f"Indexing confirmed Legionella reference: {args.ref}")
    ref_hashes, n_ref = build_ref_hashes(args.ref, args.rc)
    print(f"Loaded {n_ref} reference records; unique sequence hashes = {len(ref_hashes)}")

    os.makedirs(args.outdir, exist_ok=True)

    summary_path = Path(args.outdir) / "summary.tsv"

    with open(summary_path, "w") as summary:
        summary.write("sample\tn_input\tn_confirmed_legionella\tfasta_file\n")

        for path in sample_paths:
            print(f"Scanning {path} ...")
            sample, total, hits, out_path = process_one(
                path,
                ref_hashes,
                args.outdir,
                args.rc
            )

            summary.write(f"{sample}\t{total}\t{hits}\t{out_path}\n")
            print(f"{sample}: {hits}/{total} confirmed Legionella records -> {out_path}")

    print(f"Summary written to {summary_path}")


if __name__ == "__main__":
    main()