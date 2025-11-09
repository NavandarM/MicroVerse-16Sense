# MicroVerse-16Sense: <h3>A snakemake workflow for processing 16s ONT data</h3>

Usages: snakemake -s Snakefile.smk   --use-conda

Requirements:
- Singularity or docker
- Edit and update the config file


You can also use the individual scripts to perform **abundance**, **alpha diversity**, and **beta diversity** analyses.

###Abundance Plot

**Script:**  
`script/plot_abundance.py`

**Usage:**  
```bash
python script/plot_abundance.py <input_dir> <output_dir> [top_n]
```
**Example**
`python script/plot_abundance.py data/kraken_reports/ results/ 10`

**Description:**  
Reads **Bracken/Kraken2** report files (`*.kraken2_bracken.report`) from a directory, aggregates **species-level abundances**, and generates:  
- A **combined count table** (for DESeq2 or downstream analyses)  
- A **stacked bar plot** showing the top 10 most abundant species per sample  

---

### Alpha Diversity
**Script:**  
`script/alpha_diversity.py`

**Usage:**  
```bash
python script/alpha_diversity.py <abundance_file> <metadata_file> <output_dir> [group_col] [show_pvalues]
```
**Example:**
`python script/alpha_diversity.py data/abundance.tsv data/metadata.tsv results/ Group 1`

**Description:**  
Calculates alpha diversity metrics (**Shannon**, **Simpson**, **Observed**, **Chao1**) from a species abundance table, and generates grouped boxplots with optional p-value annotations.



### Beta Diversity

**Script:**  
`script/beta_diversity.py`


**Usage:**  
```bash
python script/beta_diversity.py <abundance_file> <metadata_file> <output_dir> [group_col] [metrics_comma_separated] [clr_flags_comma_separated]
```
**Example**
`python script/beta_diversity.py data/abundance.tsv data/metadata.tsv results/ Group braycurtis,jaccard,euclidean false,false,false`

**Description:**  
Computes beta diversity metrics (**Bray–Curtis**, **Jaccard**, **Euclidean**, and **UniFrac**) from an abundance table, performs **Principal Coordinates Analysis (PCoA)**, and plots PCoA scatterplots with non-overlapping sample labels.

