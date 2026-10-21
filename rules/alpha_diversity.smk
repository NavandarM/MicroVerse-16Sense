rule alpha_diversity:
    input:
        os.path.join(flags_dir, "abundance.done")
    output:
        flag = os.path.join(flags_dir, "alpha_diversity.done")
    conda:
        "../envs/diversity_env.yaml"
    params:
        script = os.path.join(scripts_dir, "alpha_diversity.py"),
        abund = os.path.join(output_dir, "abundance_table_species.tsv"),
        meta = config["metadata_file"],
        group_col = "Group",
        outdir = results_dir,
        show_pvalues = 1
    shell:
        """
        mkdir -p {params.outdir:q}
        python {params.script:q} {params.abund:q} {params.meta:q} {params.outdir:q} {params.group_col:q} {params.show_pvalues}
        touch {output.flag:q}
        """
