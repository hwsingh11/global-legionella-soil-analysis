#!/bin/bash

# Run BLASTN against custom Legionella/Coxiellaceae/Gammaproteobacteria database

# Activate BLAST environment
source ~/miniconda3/etc/profile.d/conda.sh
conda activate blastenv

# Input/output paths
QUERY_DIR="../../data/overlaps_finaldeblur"
DB_FASTA="../../data/reference_database/final_db_both_dir.fasta"
OUT_DIR="../../data/blast_results"

mkdir -p "$OUT_DIR"

# Build BLAST database
makeblastdb \
  -in "$DB_FASTA" \
  -dbtype nucl

# Run BLAST for each filtered per-sample FASTA
for query in "$QUERY_DIR"/*.fasta; do
    filename=$(basename "$query" .fasta)

    blastn \
      -query "$query" \
      -db "$DB_FASTA" \
      -max_target_seqs 1 \
      -outfmt 10 \
      -out "$OUT_DIR/${filename}_blast.csv" \
      -strand plus

    echo "Finished BLAST for $filename"
done