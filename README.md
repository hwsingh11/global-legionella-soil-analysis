**Legionella Sequence Extraction Pipeline**

This repository documents the workflow used to detect and quantify Legionella ASVs from publicly-available soil 16S amplicon sequencing data using a two-step taxonomic classification approach.

-----------------------------------------------------------------------------

**Workflow Overview**

The pipeline consists of the following steps:

-   Metadata processing and climate variable extraction

-   Sequence processing (trimming, Deblur, VSEARCH dereplication)

-   Filtering sequences to Deblur ASVs

-   BLAST-based detection of candidate Legionella sequences

-   Extraction of candidate Legionella sequences per sample

-   Phylogenetic confirmation of Legionella ASVs

-   Extraction of confirmed Legionella sequences per sample

-   Extraction of abundance information from FASTA size= annotations

-----------------------------------------------------------------------------


**Repository Structure**

scripts/

  01_metadata_processing/
  
  02_sequence_processing/
  
  03_legionella_detection/
  
  04_abundance_tables/


Note: Raw sequence data and intermediate FASTA files are not included due to size constraints.

-----------------------------------------------------------------------------



**01. Metadata Processing**

Extract climate variables from WorldClim:

    Rscript scripts/01_metadata_processing/extract_worldclim_climate.R

    Input: metadata_coord.csv

    Output: metadata_coord_with_worldclim.csv

This script extracts:

-   Monthly temperature for exact collection dates

-   Mean temperature (2016–2018) for range-based samples

-   Annual precipitation

-----------------------------------------------------------------------------

**02. Sequence Processing**

Trim sequences to 150 bp

    bash scripts/02_sequence_processing/trim_sequences_150bp.sh

Run Deblur

    bash scripts/02_sequence_processing/run_deblur.sh

Dereplicate sequences (VSEARCH)

    bash scripts/02_sequence_processing/run_vsearch_dereplication.sh

Generate database list

    bash scripts/02_sequence_processing/create_db_list.sh
    This creates: data/vsearch_dereplicated/db_list.txt

Filter to Deblur ASVs

    bash scripts/02_sequence_processing/run_filter_to_deblur_asvs.sh

-----------------------------------------------------------------------------


**03. Legionella Detection**

Run BLAST against custom database

    bash scripts/03_legionella_detection/run_custom_blast.sh
    Uses custom database: data/reference_database/final_db_both_dir.fasta


Extract candidate Legionella sequences

    bash scripts/03_legionella_detection/run_extract_blast_legionella_hits.sh
    
    This step: 
      - Filters BLAST results using prefix f_leg_
      - Extracts sequences matching prefix per sample

Phylogenetic confirmation (manual step)

Candidate Legionella sequences were:
- Combined across samples
- Phylogenetically placed using PhyML
- Manually filtered to retain sequences within the Legionella clade
- Clustered at 99% identity
- Singleton clusters removed

This produces:

      data/reference_database/confirmed_leg_asvs_remove_99percent_singletons.fasta
      See: scripts/03_legionella_detection/README_confirmed_legionella_reference.md

Extract confirmed Legionella sequences

    bash scripts/03_legionella_detection/run_extract_confirmed_legionella_asvs.sh
    Output: data/confirmed_legionella_fastas/
    --------------------------------------------------------
    Each file contains:
      - Only phylogenetically confirmed Legionella sequences
      - Original FASTA headers (including size= abundance values)

-----------------------------------------------------------------------------


**04. Abundance Extraction**

Extract counts from FASTA headers:

    bash scripts/04_abundance_tables/run_extract_confirmed_legionella_counts.sh
    Output: data/confirmed_legionella_counts.tsv
    --------------------------------------------------------
    Format:
    sample    asv_id    count
    Counts are derived from size= annotations in FASTA headers.
    
-----------------------------------------------------------------------------
**Data Availability**

Intermediate files (e.g., trimmed FASTA, Deblur outputs, dereplicated FASTAs) are not included due to size.

All steps required to regenerate these files are documented in the scripts/ directory.

db_list.txt is not included because it depends on intermediate FASTA files.
It can be regenerated using:
bash scripts/02_sequence_processing/create_db_list.sh

Downstream microbiome analyses were performed using standard workflows.

For questions, please contact **hwsingh@hawaii.edu**
