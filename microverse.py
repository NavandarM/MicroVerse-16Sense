#!/usr/bin/env python3
"""MicroVerse-16Sense: 16S ONT pipeline (epi2me wf-metagenomics + abundance/diversity plots).

Steps run in order: epi2me -> abundance -> alpha_diversity -> beta_diversity.
A finished step leaves <output_dir>/flags/<step>.done and is skipped on the next
run; once a step is (re)run, every step after it is rerun as well.
"""

import argparse
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent
SCRIPTS = REPO / "scripts"
ENVS = REPO / "envs"

STEPS = ["epi2me", "abundance", "alpha_diversity", "beta_diversity"]
STEP_ENV = {
    "epi2me": "nextflow_env.yaml",
    "abundance": "plotting_env.yaml",
    "alpha_diversity": "diversity_env.yaml",
    "beta_diversity": "diversity_env.yaml",
}


def load_config(path):
    with open(path) as fh:
        cfg = yaml.safe_load(fh) or {}
    for key in ("input_dir", "output_dir", "metadata_file"):
        if not cfg.get(key):
            sys.exit(f"config: '{key}' is required")
    cfg["output_dir"] = Path(cfg["output_dir"])
    return cfg


def build_command(step, cfg):
    out = cfg["output_dir"]
    results = out / "results"
    abund = out / "abundance_table_species.tsv"
    group_col = cfg.get("group_col", "Group")

    if step == "epi2me":
        cmd = ["nextflow", "-log", str(out / "log" / "nextflow.log"),
               "run", "epi2me-labs/wf-metagenomics"]
        if cfg.get("nextflow_config"):
            cmd += ["-c", cfg["nextflow_config"]]
        cmd += ["-profile", cfg.get("profile_tool", "singularity"),
                "-work-dir", str(out / "nf_work"),
                "-resume", "-ansi-log", "false",
                "--fastq", str(cfg["input_dir"]),
                "--out_dir", str(out),
                "--kraken2_memory_mapping",
                "--keep_bam", "true"]
        for key, opt in (("database_dir", "--database"),
                         ("taxonomy_dir", "--taxonomy"),
                         ("storage_dir", "--store_dir")):
            if cfg.get(key):
                cmd += [opt, str(cfg[key])]
        return cmd

    if step == "abundance":
        return ["python", str(SCRIPTS / "plot_abundance.py"),
                str(out / "bracken"), str(results), str(cfg.get("top_n", 10))]

    if step == "alpha_diversity":
        return ["python", str(SCRIPTS / "alpha_diversity.py"),
                str(abund), cfg["metadata_file"], str(results), group_col,
                "1" if cfg.get("show_pvalues", True) else "0"]

    if step == "beta_diversity":
        return ["python", str(SCRIPTS / "beta_diversity.py"),
                str(abund), cfg["metadata_file"], str(results), group_col,
                cfg.get("beta_metrics", "braycurtis,jaccard,euclidean"),
                cfg.get("clr_flags", "False,False,False")]

    raise ValueError(step)


def conda_exe():
    # plain conda: recent versions use the libmamba solver anyway, and a
    # standalone mamba is often out of sync with the installed conda
    if shutil.which("conda"):
        return "conda"
    sys.exit("conda not found; install it or run with --no-conda")


def ensure_env(env_yaml, env_dir, dry_run):
    """Create the conda env for env_yaml once; a changed yaml gets a new env."""
    digest = hashlib.md5(env_yaml.read_bytes()).hexdigest()[:8]
    prefix = env_dir / f"{env_yaml.stem}-{digest}"
    if not prefix.exists():
        cmd = [conda_exe(), "env", "create", "-p", str(prefix), "-f", str(env_yaml)]
        print(f"[env] creating {prefix}", flush=True)
        if not dry_run:
            subprocess.run(cmd, check=True)
    return prefix


def run_step(step, cfg, args):
    cmd = build_command(step, cfg)
    if not args.no_conda:
        prefix = ensure_env(ENVS / STEP_ENV[step], args.env_dir, args.dry_run)
        cmd = ["conda", "run", "--no-capture-output", "-p", str(prefix)] + cmd

    print(f"\n[{step}] {' '.join(cmd)}", flush=True)
    if args.dry_run:
        return

    out = cfg["output_dir"]
    for d in ("log", "nf_work", "results", "flags"):
        (out / d).mkdir(parents=True, exist_ok=True)

    result = subprocess.run(cmd, cwd=REPO)
    if result.returncode != 0:
        sys.exit(f"[{step}] failed with exit code {result.returncode}")
    (out / "flags" / f"{step}.done").touch()


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-c", "--config", default=str(REPO / "config.yaml"),
                        help="config file (default: config.yaml next to this script)")
    parser.add_argument("--steps", nargs="+", choices=STEPS, default=STEPS,
                        help="only run these steps (default: all)")
    parser.add_argument("--force", action="store_true",
                        help="rerun steps even if their .done flag exists")
    parser.add_argument("--no-conda", action="store_true",
                        help="use tools from the current environment instead of envs/*.yaml")
    parser.add_argument("--env-dir", type=Path, default=REPO / ".conda_envs",
                        help="where the conda envs are created (default: .conda_envs/)")
    parser.add_argument("-n", "--dry-run", action="store_true",
                        help="print the commands without running them")
    args = parser.parse_args()

    cfg = load_config(args.config)
    flags = cfg["output_dir"] / "flags"

    rerun = args.force
    for step in STEPS:
        if step not in args.steps:
            continue
        if not rerun and (flags / f"{step}.done").exists():
            print(f"[{step}] already done, skipping")
            continue
        run_step(step, cfg, args)
        rerun = True

    print("\nDone." if not args.dry_run else "\nDry run, nothing executed.")


if __name__ == "__main__":
    main()
