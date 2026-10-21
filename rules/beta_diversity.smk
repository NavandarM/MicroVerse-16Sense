rule beta_diversity:
    input:
        os.path.join(flags_dir, "alpha_diversity.done")
    output:
        flag = os.path.join(flags_dir, "beta_diversity.done")
    conda:
        "../envs/diversity_env.yaml"
    params:
        script = os.path.join(scripts_dir, "beta_diversity.py"),
        abund = os.path.join(output_dir, "abundance_table_species.tsv"),
        meta = config["metadata_file"],
        outdir = results_dir,
        group_col = "Group",
        metrics = "braycurtis,jaccard,euclidean",
        clr_flags = "False,False,True"
    shell:
        """
        mkdir -p {params.outdir:q}
        python {params.script:q} {params.abund:q} {params.meta:q} {params.outdir:q} {params.group_col:q} {params.metrics:q} {params.clr_flags:q}
        touch {output.flag:q}
        """
