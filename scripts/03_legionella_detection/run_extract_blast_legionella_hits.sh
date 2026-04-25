#!/bin/bash

python extract_blast_legionella_hits.py \
  --blast_dir "../../data/blast_results" \
  --fasta_dir "../../data/overlaps_finaldeblur" \
  --outdir "../../data/candidate_legionella_hits" \
  --hit_prefix "f_leg_"