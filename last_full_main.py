import subprocess
import sys
import os
import importlib.util
import yaml

# ---------------------------------------------------------------
# Utility: run PowerShell script
# ---------------------------------------------------------------
def run_ps(script_path):
    print(f"\n[RUN] PowerShell Script: {script_path}")
    completed = subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path]
    )
    if completed.returncode != 0:
        print(f"[ERROR] Script failed: {script_path}")
        sys.exit(1)

# ---------------------------------------------------------------
# Utility: run Python script with return value
# ---------------------------------------------------------------
def run_py_with_return(script_path, function_name="run", *args):
    spec = importlib.util.spec_from_file_location("module", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    func = getattr(module, function_name)
    return func(*args)

# ---------------------------------------------------------------
# Utility: run Python script without return value
# ---------------------------------------------------------------
def run_py(script_path, function_name="run"):
    spec = importlib.util.spec_from_file_location("module", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    func = getattr(module, function_name)
    func()

# ---------------------------------------------------------------
# Path initialization (asks user and updates config.yaml)
# ---------------------------------------------------------------
def initialize_paths(config_path):
    print("\n============================================================")
    print("Path Setup - confirm or override source/target paths")
    print("============================================================")

    ROOT = os.path.dirname(os.path.abspath(__file__))
    guessed_source = os.path.join(ROOT, "input")
    guessed_target = os.path.join(ROOT, "output")

    print(f"Detected default source: {guessed_source}")
    print(f"Detected default target: {guessed_target}")

    ans = input("\nAre these paths correct? (y/n): ").strip().lower()
    if ans != "y":
        print("\nEnter custom paths (absolute or relative). Press ENTER to accept default.")
        src = input(f"Source path [{guessed_source}]: ").strip()
        tgt = input(f"Target path [{guessed_target}]: ").strip()
        if src:
            guessed_source = src
        if tgt:
            guessed_target = tgt

    # Normalize to absolute
    guessed_source = os.path.abspath(guessed_source)
    guessed_target = os.path.abspath(guessed_target)

    os.makedirs(guessed_source, exist_ok=True)
    os.makedirs(guessed_target, exist_ok=True)

    # Ensure config exists
    if not os.path.exists(config_path):
        # create minimal config
        cfg = {
            "dialect": "synapse",
            "profile": "lakebridge",
            "debug": False,
            "run_validation": True,
            "run_analyzer": True,
            "run_transpiler": True,
            "source_path": guessed_source,
            "target_path": guessed_target
        }
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(cfg, f, sort_keys=False)
        print(f"\nCreated config at {config_path} with detected paths.")
    else:
        # load and update
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
        cfg["source_path"] = guessed_source
        cfg["target_path"] = guessed_target
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(cfg, f, sort_keys=False)
        print(f"\nUpdated config at {config_path} with detected paths.")

    print("\nPaths set to:")
    print(f"  source_path: {guessed_source}")
    print(f"  target_path: {guessed_target}")
    print("============================================================\n")
    return guessed_source, guessed_target

# ---------------------------------------------------------------
# MAIN ORCHESTRATION
# ---------------------------------------------------------------
def main():

    ROOT = os.path.dirname(os.path.abspath(__file__))

    PS_PREFLIGHT = f"{ROOT}/scripts/preflight/preflight_interactive.ps1"
    PS_INSTALL   = f"{ROOT}/scripts/install/install_lakebridge.ps1"

    PY_STEPS = f"{ROOT}/scripts/python_steps"

    # Steps - 3 and 4 removed from flow
    STEP5 = f"{PY_STEPS}/step5_preprocess.py"
    STEP6 = f"{PY_STEPS}/step6_core_engine.py"  # will be executed as separate process
    STEP7 = f"{PY_STEPS}/step7_postprocess.py"
    STEP8 = f"{PY_STEPS}/step8_output_handler.py"

    config_file = os.path.join(ROOT, "config", "config.yaml")
    os.makedirs(os.path.dirname(config_file), exist_ok=True)

    print("============================================================")
    print("Lakebridge Accelerator - Main Orchestrator (New Flow)")
    print("============================================================")

    # STEP 1 - Preflight
    print("\nSTEP 1 - Preflight Checks")
    run_ps(PS_PREFLIGHT)

    # STEP 2 - Install Lakebridge
    print("\nSTEP 2 - Lakebridge Installation")
    run_ps(PS_INSTALL)

    # STEP 2.5 - Path setup & config update (new)
    print("\nSTEP 2.5 - Path Setup (confirm or override source/target)")
    initialize_paths(config_file)

    # STEP 5 - Pre-processing (reads config)
    print("\nSTEP 5 - Pre-processing")
    step5_result = run_py_with_return(STEP5, "run_step5", None)
    if step5_result is None:
        print("[ERROR] Step 5 returned no data. Exiting.")
        sys.exit(1)

    # STEP 6 - Core Engine (external python process)
    print("\nSTEP 6 - Core Engine (Analyzer + Transpiler + Upload)")

    cmd = [
        sys.executable,
        STEP6,
        "--config",
        config_file
    ]
    print(f"\n[RUN] {' '.join(cmd)}\n")
    rc = subprocess.run(cmd).returncode
    if rc != 0:
        print("\n============================================================")
        print("CORE ENGINE FAILED — STOPPING PIPELINE")
        print("============================================================")
        sys.exit(1)

    # STEP 7 - Post-processing
    print("\nSTEP 7 - Post-processing")
    # call postprocess (expects to read config or step6 outputs)
    try:
        step7_result = run_py_with_return(STEP7, "run_step7", None)
    except Exception as e:
        print(f"[ERROR] Step 7 failed: {e}")
        sys.exit(1)

    # STEP 8 - Output writer
    print("\nSTEP 8 - Output Writer")
    try:
        run_py_with_return(STEP8, "run_step8", step7_result)
    except Exception as e:
        print(f"[ERROR] Step 8 failed: {e}")
        sys.exit(1)

    print("\n============================================================")
    print("All Steps Completed Successfully.")
    print("============================================================")

if __name__ == "__main__":
    main()