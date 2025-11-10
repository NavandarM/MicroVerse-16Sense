# MicroVerse-16Sense: <h3>A snakemake workflow for processing 16s ONT data</h3>

Usages: 
```bash
snakemake -s Snakefile.smk   --use-conda
```
Requirements:
- Singularity or docker
- Edit and update the config file

---
Apart from the pipeline, you can also use the individual scripts to perform **abundance**, **alpha diversity**, and **beta diversity** analyses.

###Abundance Plot

**Script:**  
`script/plot_abundance.py`

**Usage:**  
```bash
python script/plot_abundance.py <input_dir> <output_dir> [top_n]
```
Inputs:
- input_dir: Path to the directory containing *.kraken2_bracken.report files.
- output_dir: Directory to save the results.
- top_n (default = 10): Number of top species to display in the stacked bar plot. (optional) <br>

Output:
- raw_counts_for_deseq2.txt: Combined species-level count table for all samples.
- composition_plot.pdf: Stacked bar plot showing relative abundances of the top species across samples, saved in the specified output directory.

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

Inputs:
- abundance_file: Tab-delimited table of species/OTU counts (rows = species, columns = samples).
- metadata_file: Tab-delimited metadata linking samples to experimental groups.
- output_dir: Directory for saving results.
- group_col (default = "Group"): Column in metadata to define sample groups. (optional)
- show_pvalues (default = 0): Whether to display p-values on the plots (0 = no, 1 = yes). (optional)

Output:
- alpha_diversity_plots.pdf or alpha_diversity_with_pvalues.pdf: Boxplots summarizing alpha diversity metrics (Shannon, Simpson, Observed OTUs, Chao1) per sample group.

**Description:**  
Calculates alpha diversity metrics (**Shannon**, **Simpson**, **Observed**, **Chao1**) from a species abundance table, and generates grouped boxplots with optional p-value annotations.

---

### Beta Diversity

**Script:**  
`script/beta_diversity.py`


**Usage:**  
```bash
python script/beta_diversity.py <abundance_file> <metadata_file> <output_dir> [group_col] [metrics_comma_separated] [clr_flags_comma_separated]
```
**Example**
`python script/beta_diversity.py data/abundance.tsv data/metadata.tsv results/ Group braycurtis,jaccard,euclidean false,false,false`

Inputs:
- abundance_file: Tab-delimited table of species/OTU counts (rows = species, columns = samples).
- metadata_file: Tab-delimited metadata linking samples to experimental groups.
- output_dir: Directory to save results.
- group_col (default = "Group"): Column in metadata for grouping samples. (optional)
- metrics_comma_separated (default = "braycurtis,jaccard,euclidean"): Beta diversity metrics to compute. (optional)
- clr_flags_comma_separated (default = false,false,false): Whether to apply CLR transformation for each metric (true or false). (optional)

Output:
- beta_diversity_plots.pdf: PCoA scatterplots for the selected beta diversity metrics, colored by sample group, saved in the specified output directory.
  
**Description:**  
Computes beta diversity metrics (**Bray–Curtis**, **Jaccard**, **Euclidean**, and **UniFrac**) from an abundance table, performs **Principal Coordinates Analysis (PCoA)**, and plots PCoA scatterplots with non-overlapping sample labels.

