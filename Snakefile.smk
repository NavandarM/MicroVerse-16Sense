configfile: "config.yaml"

include: "rules/setup_env.smk"
include: "rules/run_metagenomics.smk"

rule all:
    input:
        expand("{output_dir}/workflow_complete.txt", output_dir=config["output_dir"])

