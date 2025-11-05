#!/usr/bin/env python3
"""
plot_abundance.py

Reads Bracken/Kraken2 output reports (*.kraken2_bracken.report) from a directory,
aggregates species-level abundances, generates:
    - a combined count table for DESeq2
    - a stacked bar plot of top 10 species.
"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt


def main(input_dir: str, output_dir: str, top_n: int = 10):
    """
    input_dir :  Path to folder containing *.kraken2_bracken.report files.
    output_dir : Directory to write results.
    top_n :  Number of top species to plot.
    """

    file_suffix = ".kraken2_bracken.report"
    files = sorted([f for f in os.listdir(input_dir) if f.endswith(file_suffix)])

    if not files:
        sys.exit(f"No files ending with {file_suffix} found in {input_dir}")

    abundance_data = {}
    raw_counts = {}

    for file in files:
        sample_name = file.replace(file_suffix, "")
        path = os.path.join(input_dir, file)
        df = pd.read_csv(path, sep="\t", comment="#")

        species_df = (
            df[df["taxonomy_lvl"] == "S"][["name", "fraction_total_reads"]]
            .groupby("name")
            .sum(numeric_only=True)["fraction_total_reads"]
        )
        abundance_data[sample_name] = species_df

        species_count = (
            df[df["taxonomy_lvl"] == "S"][["name", "new_est_reads"]]
            .groupby("name")
            .sum(numeric_only=True)["new_est_reads"]
        )
        raw_counts[sample_name] = species_count

    combined_df = pd.DataFrame(abundance_data).fillna(0)
    combined_counts = pd.DataFrame(raw_counts).fillna(0).astype(int)

    os.makedirs(output_dir, exist_ok=True)

    counts_path = os.path.join(output_dir, "raw_counts_for_deseq2.txt")
    combined_counts.to_csv(counts_path, sep="\t", index=True)

    # plotting ...
    top_species = combined_df.sum(axis=1).sort_values(ascending=False).head(top_n).index
    other = combined_df[~combined_df.index.isin(top_species)].sum()
    filtered_df = combined_df.loc[top_species]
    filtered_df.loc["Other"] = other
    plot_df = filtered_df.T

    plt.figure(figsize=(12, 7))
    plot_df.plot(kind="bar", stacked=True, colormap="tab20")
    plt.ylabel("Relative abundance (%)")
    plt.xlabel("Sample")
    plt.title(f"Top {top_n} Species-level Composition")
    plt.xticks(rotation=45, ha="right")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left", title="Species")
    plt.tight_layout()
    plot_path = os.path.join(output_dir, f"composition_plot.pdf")
    plt.savefig(plot_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {counts_path}")
    print(f"Saved: {plot_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit("Usage: plot_abundance.py <input_dir> <output_dir> [top_n]")
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    top_n = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    main(input_dir, output_dir, top_n)