import subprocess
import sys
import os
import importlib.util

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
    # Dynamically load module
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
# MAIN ORCHESTRATION
# ---------------------------------------------------------------
def main():
    ROOT = os.path.dirname(os.path.abspath(__file__))
    PS_PREFLIGHT = f"{ROOT}/scripts/preflight/preflight_interactive.ps1"
    PS_INSTALL   = f"{ROOT}/scripts/install/install_lakebridge.ps1"

    PY_STEPS = f"{ROOT}/scripts/python_steps"

    STEP3 = f"{PY_STEPS}/step3_folder_setup.py"
    STEP4 = f"{PY_STEPS}/step4_input_selection.py"
    STEP5 = f"{PY_STEPS}/step5_preprocess.py"
    STEP6 = f"{PY_STEPS}/step6_core_engine.py"
    STEP7 = f"{PY_STEPS}/step7_postprocess.py"
    STEP8 = f"{PY_STEPS}/step8_output_handler.py"

    print("============================================================")
    print("Lakebridge Accelerator - Main Orchestrator")
    print("============================================================")

    # -----------------------------------------------------------
    # STEP 1 - Preflight (PowerShell)
    # -----------------------------------------------------------
    print("\nSTEP 1 - Preflight Checks")
    run_ps(PS_PREFLIGHT)

    # -----------------------------------------------------------
    # STEP 2 - Installation (PowerShell)
    # -----------------------------------------------------------
    print("\nSTEP 2 - Lakebridge Installation")
    run_ps(PS_INSTALL)

    # -----------------------------------------------------------
    # STEP 3 - Folder Setup (Python)
    # -----------------------------------------------------------
    print("\nSTEP 3 - Folder Structure Setup")
    run_py(STEP3, "run_step3")

    # -----------------------------------------------------------
    # STEP 4 - Input Selection (Python returns selection dict)
    # -----------------------------------------------------------
    print("\nSTEP 4 - Input Selection")
    step4_result = run_py_with_return(STEP4, "run_step4")
    if step4_result is None:
        print("[ERROR] Step 4 returned no data. Exiting.")
        sys.exit(1)

    # -----------------------------------------------------------
    # STEP 5 - Pre-processing (Python)
    # -----------------------------------------------------------
    print("\nSTEP 5 - Pre-processing")
    step5_result = run_py_with_return(STEP5, "run_step5", step4_result)
    if step5_result is None:
        print("[ERROR] Step 5 returned no data. Exiting.")
        sys.exit(1)

    # -----------------------------------------------------------
    # STEP 6 - Core Engine (Analyzer + Transpiler)
    # -----------------------------------------------------------
    print("\nSTEP 6 - Core Engine")
    step6_result = run_py_with_return(STEP6, "run_step6", step5_result)

    if not step6_result or not step6_result.get("success", False):
        print("\n============================================================")
        print("CORE ENGINE FAILED — STOPPING PIPELINE")
        print("============================================================")

        if step6_result:
            print(f"Failed at Stage: {step6_result.get('step')}")
            print(f"Return code: {step6_result.get('returncode')}")
            print("Stdout:\n", step6_result.get("stdout"))
            print("Stderr:\n", step6_result.get("stderr"))
            print("Analyzer Report:", step6_result.get("analyzer_report"))
            print("Transpile Output Folder:", step6_result.get("transpile_output_folder"))

        print("\nExiting with failure status.")
        sys.exit(1)


    # -----------------------------------------------------------
    # STEP 7 - Post-processing (Python)
    # -----------------------------------------------------------
    print("\nSTEP 7 - Post-processing")
    step7_result = run_py_with_return(STEP7, "run_step7", step6_result)

    # -----------------------------------------------------------
    # STEP 8 - Output Handling (Python)
    # -----------------------------------------------------------
    print("\nSTEP 8 - Output Writer")
    run_py_with_return(STEP8, "run_step8", step7_result)

    print("\n============================================================")
    print("All Steps Completed Successfully.")
    print("============================================================")

if __name__ == "__main__":
    main()
