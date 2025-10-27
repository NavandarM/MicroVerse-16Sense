rule run_wf_metagenomics:
    input:
        fastq_dir=config["input_dir"]
    output:
        touch("{output_dir}/workflow_complete.txt")
    conda:
        "envs/nextflow_env.yaml"
    shell:
        """
        nextflow run epi2me-labs/wf-metagenomics \
            --fastq {input.fastq_dir} \
            --outdir {config[output_dir]} \
            --classifier {config[classifier]} \
            --db {config[db]} \
            -profile {config[profile]}
        echo "Workflow finished" > {output}
        """

