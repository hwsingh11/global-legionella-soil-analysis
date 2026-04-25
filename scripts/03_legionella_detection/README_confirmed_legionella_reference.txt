# Confirmed Legionella ASV reference

`confirmed_leg_asvs_remove_99percent_singletons.fasta` is generated after candidate Legionella sequences are extracted from BLAST results and manually/phylogenetically confirmed.

Workflow:

1. Extract candidate Legionella hits from BLAST results.
2. Combine candidate Legionella hits into single file.
3. Screen combined file for phylogenetic placement (confirmation of whether a true Legionella hit). This database (final_db_both_dir.fasta) comprised 16S sequences from all reference-quality and complete Legionella genomes available in the NCBI database, together with all sequences from neighboring family Coxiellaceae (also within the order Legionellales), as well as a representative selection of 16S sequences spanning the broader Gammaproteobacteria and bacterial domain. Candidate sequences were then placed into a backbone phylogenetic tree constructed from this custom reference database using PhyML to confirm phylogenetic affiliation.
4. Manually retain ASVs placed within the Legionella clade.
5. Cluster into 99% OTUs and remove singleton clusters.
6. Save retained sequences as:

`data/reference_database/confirmed_leg_asvs_remove_99percent_singletons.fasta`

This file is then used to extract confirmed Legionella sequences from each per-sample FASTA while preserving `size=` abundance annotations.