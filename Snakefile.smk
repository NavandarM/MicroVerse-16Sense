configfile: "config1.yaml"

output_dir=config["output_dir"]


include: "rules/setup_env.smk"
include: "rules/run_metagenomics.smk"
include: "rules/plot_abundance.smk"
include: "rules/alpha_diversity.smk"
include: "rules/beta_diversity.smk"

rule all:
    input:
        output_dir + "flags/epi2me.done",
        output_dir + "flags/abundance.done",
        output_dir + "flags/alpha_diversity.done",
        output_dir + "flags/beta_diversity.done"