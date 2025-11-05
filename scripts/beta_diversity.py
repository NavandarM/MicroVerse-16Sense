#!/usr/bin/env python3
"""
beta_diversity.py

Compute beta diversity metrics (Bray-Curtis, Jaccard, Euclidean, UniFrac) from an abundance table,
perform PCoA, and plot PCoA coordinates with non-overlapping sample labels.
"""

import os
import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from skbio.diversity import beta_diversity
from skbio.stats.ordination import pcoa
from adjustText import adjust_text


def beta_diversity_coords(abund, meta, metric="braycurtis", group_col="Group", clr=False, tree=None):
    """
    Compute PCoA coordinates for a given beta diversity metric.

    abund : DataFrame
        Abundance table
    meta : DataFrame
        Metadata with sample IDs as index
    metric : str
        Beta diversity metric: "braycurtis", "jaccard", "euclidean", "unweighted_unifrac", "weighted_unifrac"
    group_col : str
        Metadata column to use for coloring
    clr : bool
        Apply CLR transform (for Euclidean only)
    tree : skbio.TreeNode
        Required for UniFrac metrics
    """
    data = abund.T.fillna(0).astype(float)

    if clr:
        from skbio.stats.composition import multiplicative_replacement, clr
        data = pd.DataFrame(
            clr(multiplicative_replacement(data)),
            index=data.index,
            columns=data.columns
        )

    if metric in ["unweighted_unifrac", "weighted_unifrac"]:
        if tree is None:
            raise ValueError(f"{metric} requires a phylogenetic tree (skbio.TreeNode).")
        dm = beta_diversity(metric, data.values, ids=data.index, tree=tree)
    else:
        dm = beta_diversity(metric, data.values, ids=data.index)

    ord_res = pcoa(dm)
    coords = ord_res.samples
    var_exp = ord_res.proportion_explained * 100
    coords = coords.join(meta, how="left")
    return coords, var_exp


def plot_beta_diversity(abund, meta, output_dir, metrics, clr_flags, group_col="Group"):
    sns.set(style="whitegrid", font_scale=1.2)
    n = len(metrics)
    ncols = 2
    nrows = (n + 1) // 2
    fig, axes = plt.subplots(nrows, ncols, figsize=(12, 5 * nrows))
    axes = axes.flatten()

    for i, (metric, clr_flag) in enumerate(zip(metrics, clr_flags)):
        coords, var_exp = beta_diversity_coords(
            abund=abund,
            meta=meta,
            metric=metric,
            group_col=group_col,
            clr=clr_flag
        )

        sns.scatterplot(
            data=coords,
            x="PC1", y="PC2",
            hue=group_col, style=group_col,
            s=80, alpha=0.8, palette="Set2", ax=axes[i]
        )

        #non-overlapping labs
        texts = []
        for sample_id, x, y in zip(coords.index, coords['PC1'], coords['PC2']):
            texts.append(axes[i].text(x, y, sample_id, fontsize=8))
        adjust_text(texts, ax=axes[i], arrowprops=dict(arrowstyle="-", color='gray', lw=0.5))

        axes[i].set_xlabel(f"PC1 ({var_exp['PC1']:.2f}%)")
        axes[i].set_ylabel(f"PC2 ({var_exp['PC2']:.2f}%)")
        axes[i].set_title(f"PCoA - {metric}")
        axes[i].axhline(0, color="gray", ls="--", lw=0.5)
        axes[i].axvline(0, color="gray", ls="--", lw=0.5)

    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    plt.tight_layout()
    output_file = os.path.join(output_dir, "beta_diversity_plots.pdf")
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Beta diversity plots saved -->  {output_file}")


def main(abundance_file, metadata_file, output_dir, group_col="Group", metrics=None, clr_flags=None):
    # Load data
    abund = pd.read_csv(abundance_file, index_col=0, sep='\t')
    abund = abund.drop(abund.columns[-1], axis=1)
    meta = pd.read_csv(metadata_file, index_col=0, sep='\t')

    if metrics is None:
        metrics = ["braycurtis", "jaccard", "euclidean"]
    if clr_flags is None:
        clr_flags = [False] * len(metrics)
    if len(metrics) != len(clr_flags):
        raise ValueError("metrics and clr_flags must be the same length")

    plot_beta_diversity(abund, meta, output_dir, metrics, clr_flags, group_col)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit("Usage: beta_diversity.py <abundance_file> <metadata_file> <output_dir> [group_col] [metrics_comma_separated] [clr_flags_comma_separated]")
    
    abundance_file = sys.argv[1]
    metadata_file = sys.argv[2]
    output_dir = sys.argv[3]
    group_col = sys.argv[4] if len(sys.argv) > 4 else "Group"

    metrics = sys.argv[5].split(",") if len(sys.argv) > 5 else ["braycurtis", "jaccard", "euclidean"]
    clr_flags = [flag.lower() in ("1", "true", "yes") for flag in sys.argv[6].split(",")] if len(sys.argv) > 6 else [False] * len(metrics)

    main(abundance_file, metadata_file, output_dir, group_col, metrics, clr_flags)
