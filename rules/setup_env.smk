rule pull_wf_metagenomics:
    conda:
        "../envs/nextflow_env.yaml"
    output:
        touch("logs/wf_pulled.txt")
    shell:
        """
        mkdir -p logs
        rm -rf ~/.nextflow/assets/epi2me-labs/wf-metagenomics || true
        nextflow pull epi2me-labs/wf-metagenomics || nextflow pull https://github.com/epi2me-labs/wf-metagenomics
        echo "wf-metagenomics pulled successfully" > {output}
        """

