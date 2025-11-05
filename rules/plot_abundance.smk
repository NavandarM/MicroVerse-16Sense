rule plot_abundance:
    input:
        output_dir + "flags/epi2me.done"
    output:
        results_fag = output_dir + "flags/abundance.done"
    conda:
        "../envs/plotting_env.yaml"
    params:
        reports_dir = output_dir + "bracken/",
        top=10
    shell:
        """
        mkdir -p {output_dir}/results
        python scripts/plot_abundance.py {params.reports_dir} {output_dir}/results {params.top}
        touch {output.results_fag}
        """