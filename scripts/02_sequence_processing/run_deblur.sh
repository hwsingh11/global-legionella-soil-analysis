#!/bin/bash

# Activate QIIME2 environment (contains Deblur)
source ~/miniconda3/etc/profile.d/conda.sh
conda activate qiime2-amplicon-2024.10

# Run Deblur denoising on 150-bp trimmed FASTA files

INPUT_DIR="../../data/trimmed_150bp"
OUTPUT_DIR="../../data/deblur_out"

mkdir -p "$OUTPUT_DIR"

deblur workflow \
  --seqs-fp "$INPUT_DIR" \
  --output-dir "$OUTPUT_DIR" \
  --trim-length -1 \
  --overwrite \
  --min-reads 0 \
  --min-size 1