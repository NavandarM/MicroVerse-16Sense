rule alpha_diversity:
    input:
        output_dir + "flags/abundance.done"
    output:
        flag = output_dir + "flags/alpha_diversity.done"
    conda:
        "../envs/diversity_env.yaml"
    params:
        abund = output_dir + "abundance_table_species.tsv",
        meta = config['metadata_file'],
        group_col = "Group",
        outdir = output_dir + "results",
        show_pvalues= 1
    shell:
        """
        python scripts/alpha_diversity.py {params.abund} {params.meta} {params.outdir}  {params.group_col} {params.show_pvalues}
        touch {output.flag}
        """