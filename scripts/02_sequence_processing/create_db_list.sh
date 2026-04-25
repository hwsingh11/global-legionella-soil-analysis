#!/bin/bash

INPUT_DIR="../../data/vsearch_dereplicated"
OUTPUT_FILE="$INPUT_DIR/db_list.txt"

> "$OUTPUT_FILE"

for f in "$INPUT_DIR"/*_centroids.fasta; do
    echo "$f" >> "$OUTPUT_FILE"
done

echo "Wrote database list to $OUTPUT_FILE"