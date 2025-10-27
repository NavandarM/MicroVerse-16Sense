rule setup_env:
    conda:
        "envs/nextflow_env.yaml"
    shell:
        """
        echo "Conda environment ready with Nextflow and dependencies."
        """
