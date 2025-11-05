"""
alpha_diversity.py

Calculate alpha diversity metrics (Shannon, Simpson, Observed, Chao1) from a species abundance table,
plot boxplots by sample groups, and optionally display p-values.
"""

import os
import sys
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from skbio.diversity import alpha_diversity
from scipy.stats import mannwhitneyu, kruskal


def rarefy_counts(col, depth):
    counts = col.values.astype(int)
    if counts.sum() < depth:
        return np.nan * np.ones_like(counts)
    idx = np.repeat(np.arange(len(counts)), counts)
    choose = np.random.default_rng(1).choice(idx, size=int(depth), replace=False)
    out = np.bincount(choose, minlength=len(counts))
    return out


def compute_alpha_diversity(abund_r, meta, group_col):
    metrics = ['shannon', 'simpson', 'observed_otus', 'chao1']
    alpha = pd.DataFrame({
        'Shannon': alpha_diversity('shannon', abund_r.T.fillna(0).astype(int).values, ids=abund_r.columns),
        'Simpson': alpha_diversity('simpson', abund_r.T.fillna(0).astype(int).values, ids=abund_r.columns),
        'Observed': alpha_diversity('observed_otus', abund_r.T.fillna(0).astype(int).values, ids=abund_r.columns),
        'Chao1': alpha_diversity('chao1', abund_r.T.fillna(0).astype(int).values, ids=abund_r.columns)
    })
    alpha = alpha.join(meta, how='left')
    return alpha


def plot_alpha_diversity(alpha, group_col="Group", output_file="alpha_diversity_plots.pdf", show_pvalues=False):
    sns.set(style="whitegrid", font_scale=1.2)
    metrics = ['Shannon', 'Simpson', 'Observed', 'Chao1']
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    for ax, metric in zip(axes.flat, metrics):
        sns.boxplot(
            x=group_col, y=metric, data=alpha,
            palette="Set2", showcaps=False, fliersize=0, ax=ax, width=0.5
        )
        sns.stripplot(
            x=group_col, y=metric, data=alpha,
            color="black", size=5, jitter=True, alpha=0.7, ax=ax
        )

        if show_pvalues:
            groups = alpha[group_col].unique()
            y_max = max(alpha[metric]) * 1.05
            if len(groups) == 2:
                g1 = alpha[alpha[group_col] == groups[0]][metric]
                g2 = alpha[alpha[group_col] == groups[1]][metric]
                stat, p_value = mannwhitneyu(g1, g2, alternative='two-sided')
                x1, x2 = 0, 1
                ax.plot([x1, x1, x2, x2], [y_max-0.02*y_max, y_max, y_max, y_max-0.02*y_max], lw=1.5, c='black')
                ax.text((x1+x2)/2, y_max, f"p = {p_value:.3e}", ha='center', va='bottom', fontsize=12)
            else:
                data = [alpha[alpha[group_col] == g][metric] for g in groups]
                stat, p_value = kruskal(*data)
                ax.text(0.5, y_max, f"p = {p_value:.3e}", ha='center', va='bottom', fontsize=12)

        ax.set_title(f"{metric} Diversity", fontsize=14)
        ax.set_xlabel(group_col)
        ax.set_ylabel(metric)

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Alpha diversity plots saved to {output_file}")


def main(abundance_file, metadata_file, output_dir, group_col="Group", show_pvalues=False):
    #Get data
    abund = pd.read_csv(abundance_file, index_col=0, sep='\t')
    abund = abund.drop(abund.columns[-1], axis=1)
    meta = pd.read_csv(metadata_file, index_col=0, sep='\t')

    # Filter samples
    totals = abund.sum(axis=1)
    present = (abund > 0).sum(axis=1)
    abund_f = abund.loc[(totals >= 20) & (present >= 2)]

    #Rarefaction
    depth = abund_f.sum(axis=0).min()
    abund_r = abund_f.apply(lambda col: pd.Series(rarefy_counts(col, depth), index=abund_f.index), axis=0)

    #Compute alpha
    alpha = compute_alpha_diversity(abund_r, meta, group_col)

    # Plot
    output_file = os.path.join(output_dir, "alpha_diversity_plots.pdf")
    if show_pvalues:
        output_file = os.path.join(output_dir, "alpha_diversity_with_pvalues.pdf")
    plot_alpha_diversity(alpha, group_col, output_file, show_pvalues)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit("Usage: alpha_diversity.py <abundance_file> <metadata_file> <output_dir> [group_col] [show_pvalues]")
    abundance_file = sys.argv[1]
    metadata_file = sys.argv[2]
    output_dir = sys.argv[3]
    group_col = sys.argv[4] if len(sys.argv) > 4 else "Group"
    show_pvalues = bool(int(sys.argv[5])) if len(sys.argv) > 5 else False
    main(abundance_file, metadata_file, output_dir, group_col, show_pvalues)