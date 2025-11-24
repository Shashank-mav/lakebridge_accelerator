import subprocess
import sys
import os

# ---------------------------------------------------------------
# ANSI Colors
# ---------------------------------------------------------------
RESET = "\033[0m"
BOLD = "\033[1m"

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
WHITE = "\033[97m"

# ---------------------------------------------------------------
# Utility: run PowerShell script
# ---------------------------------------------------------------
def run_ps(script_path):
    print(f"\n{CYAN}[RUN]{RESET} PowerShell Script: {WHITE}{script_path}{RESET}")
    completed = subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path]
    )
    if completed.returncode != 0:
        print(f"{RED}[ERROR]{RESET} Script failed: {script_path}")
        sys.exit(1)

# ---------------------------------------------------------------
# Verify installation of Analyzer & Transpiler
# ---------------------------------------------------------------
def verify_installation():
    print(f"\n{BOLD}{BLUE}STEP 3 - Verifying Installation{RESET}")

    # Check Python package installation
    try:
        import databricks.labs.lakebridge
        print(f"{GREEN}PASS:{RESET} Lakebridge Python package is installed.")
    except Exception:
        print(f"{RED}FAIL:{RESET} Lakebridge Python package NOT found.")
        sys.exit(1)

    # Check CLI
    result = subprocess.run(
        ["databricks", "labs", "lakebridge", "--help"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    if result.returncode == 0:
        print(f"{GREEN}PASS:{RESET} Databricks CLI detects Lakebridge.")
    else:
        print(f"{RED}FAIL:{RESET} Databricks CLI cannot detect lakebridge.")
        print(result.stderr)
        sys.exit(1)

    print(f"\n{GREEN}Installation Verified Successfully.{RESET}\n")

# ---------------------------------------------------------------
# MAIN ORCHESTRATION
# ---------------------------------------------------------------
def main():

    ROOT = os.path.dirname(os.path.abspath(__file__))

    PS_PREFLIGHT = f"{ROOT}/scripts/preflight/preflight_interactive.ps1"
    PS_INSTALL   = f"{ROOT}/scripts/install/install_lakebridge.ps1"

    print(f"{YELLOW}{BOLD}============================================================{RESET}")
    print(f"{BLUE}{BOLD}Lakebridge Accelerator - Stage 1 Installer{RESET}")
    print(f"{YELLOW}{BOLD}============================================================{RESET}")

    # STEP 1 - Preflight
    print(f"\n{BLUE}{BOLD}STEP 1 - Preflight Checks{RESET}")
    run_ps(PS_PREFLIGHT)

    # STEP 2 - Installation
    print(f"\n{BLUE}{BOLD}STEP 2 - Lakebridge Installation{RESET}")
    run_ps(PS_INSTALL)

    # STEP 3 - Verify Installation
    verify_installation()

    # STEP 4 - Complete
    print(f"\n{YELLOW}{BOLD}============================================================{RESET}")
    print(f"{GREEN}{BOLD}STAGE 1 COMPLETE — System is ready for Stage 2{RESET}")
    print(f"{YELLOW}{BOLD}============================================================{RESET}")

if __name__ == "__main__":
    main()
