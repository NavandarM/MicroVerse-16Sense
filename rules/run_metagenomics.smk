rule run_wf_metagenomics:
    input:
        fastq_dir=config["input_dir"]
    output:
        touch("{output_dir}/workflow_complete.txt")
    conda:
        "../envs/nextflow_env.yaml"
    shell:
        """
	echo "nextflow run epi2me-labs/wf-metagenomics \
            --fastq {input.fastq_dir} \
            --out_dir {config[output_dir]} \
            --keep_bam true -profile singularity"
        nextflow run epi2me-labs/wf-metagenomics \
            --fastq {input.fastq_dir} \
            --out_dir {config[output_dir]} \
	    --kraken2_memory_mapping \
            --keep_bam true -profile singularity

        echo "Workflow finished" > {output}
        """

