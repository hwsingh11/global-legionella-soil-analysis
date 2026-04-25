#!/bin/bash

# Filter per-sample VSEARCH sequences to retain only Deblur ASVs

# Activate environment (adjust if needed)
source ~/miniconda3/etc/profile.d/conda.sh

# If vsearch is in a different env, activate it here
# conda activate your_env

SEARCH="../../data/deblur_out/all.seqs.fa"
DB_LIST="../../data/vsearch_dereplicated/db_list.txt"
OUTDIR="../../data/overlaps_finaldeblur"

mkdir -p "$OUTDIR"

python find_overlaps_vs_finaldeblur_nouc.py \
  --search "$SEARCH" \
  --list "$DB_LIST" \
  --outdir "$OUTDIR" \
  --threads 1 \
  --strand both \
  --mode dbmatched