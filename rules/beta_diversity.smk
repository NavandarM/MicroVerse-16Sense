print( output_dir + "abundance_table_species.tsv")
rule beta_diversity:
    input:
        output_dir + "flags/alpha_diversity.done"
    output:
        flag = output_dir + "flags/beta_diversity.done"
    conda:
        "../envs/diversity_env.yaml"
    params:
        abund = output_dir + "abundance_table_species.tsv",
        meta = config["metadata_file"],
        outdir = output_dir + "results",
        group_col = "Group",
        metrics = "braycurtis,jaccard,euclidean",
        clr_flags = "False,False,False"
    shell:
        """
        python scripts/beta_diversity.py {params.abund} {params.meta} {params.outdir} {params.group_col} {params.metrics} {params.clr_flags}
        touch {output.flag}
        """
