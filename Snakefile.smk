import os

configfile: "config.yaml"


# check config early, before the long nextflow step
for key in ("input_dir", "output_dir", "metadata_file"):
    if not config.get(key):
        raise ValueError(f"config.yaml: '{key}' is required")

for key in ("input_dir", "metadata_file"):
    if not os.path.exists(config[key]):
        raise FileNotFoundError(f"config.yaml: {key} does not exist: {config[key]}")

# trailing slash is optional
output_dir = os.path.abspath(config["output_dir"])
flags_dir = os.path.join(output_dir, "flags")
results_dir = os.path.join(output_dir, "results")

# lets snakemake run from any directory
scripts_dir = os.path.join(workflow.basedir, "scripts")


include: "rules/setup_env.smk"
include: "rules/run_metagenomics.smk"
include: "rules/plot_abundance.smk"
include: "rules/alpha_diversity.smk"
include: "rules/beta_diversity.smk"

rule all:
    input:
        os.path.join(flags_dir, "epi2me.done"),
        os.path.join(flags_dir, "abundance.done"),
        os.path.join(flags_dir, "alpha_diversity.done"),
        os.path.join(flags_dir, "beta_diversity.done")
