#!/bin/bash

INDIR="../../data/confirmed_legionella_fastas"
OUT="../../data/confirmed_legionella_counts.tsv"

python extract_confirmed_legionella_counts.py \
  --indir "$INDIR" \
  --out "$OUT"