#!/bin/bash

# VSEARCH dereplication at 100% identity (per sample)

INPUT_DIR="../../data/trimmed_150bp"
OUTPUT_DIR="../../data/vsearch_dereplicated"

mkdir -p "$OUTPUT_DIR"

for file in $INPUT_DIR/*_150_filtered.fasta; do
    filename=$(basename "$file" _150_filtered.fasta)

    vsearch \
      --cluster_size "$file" \
      --id 1 \
      --strand plus \
      --sizeout \
      --centroids "$OUTPUT_DIR/${filename}_centroids.fasta"

    echo "Dereplicated $filename"
done