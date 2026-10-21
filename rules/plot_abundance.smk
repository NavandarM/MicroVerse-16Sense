rule plot_abundance:
    input:
        os.path.join(flags_dir, "epi2me.done")
    output:
        flag = os.path.join(flags_dir, "abundance.done")
    conda:
        "../envs/plotting_env.yaml"
    params:
        script = os.path.join(scripts_dir, "plot_abundance.py"),
        reports_dir = os.path.join(output_dir, "bracken"),
        outdir = results_dir,
        top = 10
    shell:
        """
        mkdir -p {params.outdir:q}
        python {params.script:q} {params.reports_dir:q} {params.outdir:q} {params.top}
        touch {output.flag:q}
        """
