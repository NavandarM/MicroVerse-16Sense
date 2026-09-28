# Snakemake hands control over to Nextflow for this rule (handover: True):
#  - the job runs on the main Snakemake host and gets all resources given to
#    Snakemake (--cores, --resources), so no other job competes with Nextflow
#  - Nextflow is free to do its own scheduling, including submitting to a
#    cluster via its own executor settings (see `nextflow_config` in config.yaml)
#  - `-resume` lets a re-run pick up from the Nextflow work dir instead of
#    starting from scratch after a failure or interruption
rule run_wf_metagenomics:
    input:
        fastq_dir=config['input_dir']
    output:
        epi2me_flag= output_dir + "flags/epi2me.done"
    log:
        output_dir + "log/nextflow.log"
    handover: True
    conda:
        "../envs/nextflow_env.yaml"
    params:
        nextflowlogs = output_dir + "log",
        database_dir = f"--database {config['database_dir']}" if config.get('database_dir') else "",
        taxonomy_dir = f"--taxonomy {config['taxonomy_dir']}" if config.get('taxonomy_dir') else "",
        profile_tool = config.get('profile_tool', "singularity"),
        work_dir = output_dir + "nf_work",
        storage_dir = f"--store_dir {config['storage_dir']}" if config.get('storage_dir') else "",
        nf_config = f"-c {config['nextflow_config']}" if config.get('nextflow_config') else ""
    shell:
        """
        echo "Here is the taxonomy"
        echo {params.taxonomy_dir}

        echo "Here is the database dir"
        echo {params.database_dir}

        mkdir -p {params.nextflowlogs}
        mkdir -p {params.work_dir}

        nextflow -log {log} run epi2me-labs/wf-metagenomics \
            {params.nf_config} \
            -profile {params.profile_tool} \
            -work-dir {params.work_dir} \
            -resume \
            -ansi-log false \
            --fastq {input.fastq_dir} \
            --out_dir {output_dir} \
            --kraken2_memory_mapping \
            {params.database_dir} {params.taxonomy_dir} \
            {params.storage_dir} \
            --keep_bam true

        touch {output.epi2me_flag}
        """
