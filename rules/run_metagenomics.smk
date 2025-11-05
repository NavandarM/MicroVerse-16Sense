rule run_wf_metagenomics:
    input:
        fastq_dir=config["input_dir"]
    output:
        epi2me_flag= output_dir + "flags/epi2me.done",
    conda:
        "../envs/nextflow_env.yaml"
    params:
        nextflowlogs = output_dir + "log"
    shell:
        """

        mkdir -p {params.nextflowlogs}

        nextflow run epi2me-labs/wf-metagenomics \
            --fastq {input.fastq_dir} \
            --out_dir {config[output_dir]} \
	        --kraken2_memory_mapping \
            --keep_bam true -profile singularity \ 
              > {params.nextflowlogs}/nextflow_run.log 2>&1
        
        touch {output.epi2me_flag}
        """