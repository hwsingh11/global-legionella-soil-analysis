#!/bin/bash

REF="../../data/reference_database/confirmed_leg_asvs_remove_99percent_singletons.fasta"
INPUT_LIST="../../data/vsearch_dereplicated/db_list.txt"
OUTDIR="../../data/confirmed_legionella_fastas"

mkdir -p "$OUTDIR"

python extract_confirmed_legionella_asvs.py \
  --ref "$REF" \
  --list "$INPUT_LIST" \
  --outdir "$OUTDIR" \
  --rc