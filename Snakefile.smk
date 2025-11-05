configfile: "config.yaml"

output_dir=config["output_dir"]


include: "rules/setup_env.smk"
include: "rules/run_metagenomics.smk"
include: "rules/plot_abundance.smk"
include: "rules/alpha_diversity.smk"
include: "rules/beta_diversity.smk"

rule all:
    input:
        output_dir + "workflow_complete.txt",
        output_dir + "results/abundance.done",
        output_dir + "results/alpha_diversity.done",
        output_dir + "results/beta_diversity.done"