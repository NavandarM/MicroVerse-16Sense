rule run_wf_metagenomics:
    input:
        fastq_dir=config['input_dir']
    output:
        epi2me_flag= output_dir + "flags/epi2me.done"
    conda:
        "../envs/nextflow_env.yaml"
    params:
        nextflowlogs = output_dir + "log",
        database_dir = f"--database {config['database_dir']}" if config['database_dir'] else "",
        taxonomy_dir = f"--taxonomy {config['taxonomy_dir']}" if config['taxonomy_dir'] else "",
        profile_tool = config['profile_tool']
        work_dir = output_dir + "nf_work",
        storage_dir = f"--store_dir {config['storage_dir']}" if config['storage_dir'] else ""
    shell:
        """
        echo "Here is the taxonomy"
        echo {params.taxonomy_dir}

        echo "Here is the database dir"
        echo {params.database_dir}

        mkdir -p {params.nextflowlogs}
        mkdir -p {params.work_dir}

        nextflow run epi2me-labs/wf-metagenomics \
            --fastq {input.fastq_dir} \
            --out_dir {output_dir} \
            -work-dir {params.work_dir} \
	        --kraken2_memory_mapping \
            {params.database_dir} {params.taxonomy_dir} \
            {params.storage_dir} \
            --keep_bam true -profile {params.profile_tool}
        
        touch {output.epi2me_flag}
        """