#!/bin/bash

INPUT_DIR="../../data/raw_fasta"
OUTPUT_DIR="../../data/trimmed_150bp"

mkdir -p $OUTPUT_DIR

for file in $INPUT_DIR/*.fasta; do
    filename=$(basename "$file" .fasta)

    # Step 1: trim to 150 bp
    seqkit subseq -r 1:150 "$file" > "$OUTPUT_DIR/${filename}_150.fasta"

    # Step 2: filter to ≥150 bp
    perl size_limit_seqs.pl "$OUTPUT_DIR/${filename}_150.fasta" 149

    # Step 3: rename final output
    mv "$OUTPUT_DIR/${filename}_150.fasta_selected" \
       "$OUTPUT_DIR/${filename}_150_filtered.fasta"

    echo "Processed $filename"
done