import os
import subprocess
import sys
import time
import json
from pathlib import Path
from typing import Dict, Any

def _ensure_dir(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)

def _run_cmd(cmd, cwd=None):
    """
    Run a command list, stream output to console, return (returncode, stdout, stderr)
    """
    print(f"\n[CMD] {' '.join(cmd)}")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd, text=True)
    stdout_lines = []
    stderr_lines = []
    # stream output
    while True:
        out = proc.stdout.readline()
        err = proc.stderr.readline()
        if out:
            stdout_lines.append(out.rstrip("\n"))
            print(out.rstrip("\n"))
        if err:
            stderr_lines.append(err.rstrip("\n"))
            print(err.rstrip("\n"), file=sys.stderr)
        if out == '' and err == '' and proc.poll() is not None:
            break
    rc = proc.poll()
    stdout = "\n".join(stdout_lines)
    stderr = "\n".join(stderr_lines)
    return rc, stdout, stderr

def run_step6(step5_result: Dict[str, Any]):
    """
    step5_result expected format:
    {
      "dialect": "synapse",
      "processed_files": { "<abs_input_path>": "<processed_sql_text>", ... },
      "output_folder": "<abs_output_folder>"
    }
    """
    print("============================================================")
    print("Lakebridge Accelerator - Core Engine (Step 6)")
    print("============================================================")

    # Validate input
    if not step5_result or "processed_files" not in step5_result or "dialect" not in step5_result:
        print("[ERROR] step5_result missing required keys")
        return None

    dialect = step5_result["dialect"]
    processed_files: Dict[str, str] = step5_result["processed_files"]
    output_folder = step5_result.get("output_folder")
    if not output_folder:
        print("[ERROR] output_folder not provided in step5_result")
        return None

    root_dir = Path(__file__).resolve().parents[2]  # two levels up to project root
    temp_root = root_dir / "temp" / "step6_inputs"
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    temp_dir = temp_root / timestamp
    _ensure_dir(str(temp_dir))

    # 1) Write processed SQLs to temp_dir
    input_file_paths = []
    print(f"\nWriting processed SQL files to temp input directory: {temp_dir}")
    for src_path, sql_text in processed_files.items():
        # derive filename from original file path
        filename = Path(src_path).name
        target_path = temp_dir / filename
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(sql_text)
        input_file_paths.append(str(target_path))
        print(f"  Wrote: {target_path}")

    # 2) Prepare analyzer report path
    logs_dir = root_dir / "logs"
    _ensure_dir(str(logs_dir))
    analyzer_report = logs_dir / f"analyzer_report_{timestamp}.json"

    # Analyzer command:
    # databricks labs lakebridge analyze [--source-directory <absolute-path>] [--report-file <absolute-path>] [--source-tech <string>]
    analyzer_cmd = [
        "databricks", "labs", "lakebridge", "analyze",
        "--source-directory", str(temp_dir),
        "--report-file", str(analyzer_report),
        "--source-tech", "Synapse"
    ]

    print("\nRunning Analyzer...")
    rc, stdout, stderr = _run_cmd(analyzer_cmd)
    if rc != 0:
        print("\n[ERROR] Analyzer failed. See stderr above.")
        return {
            "success": False,
            "step": "analyze",
            "returncode": rc,
            "stdout": stdout,
            "stderr": stderr,
            "analyzer_report": str(analyzer_report)
        }

    print(f"\nAnalyzer finished successfully. Report saved: {analyzer_report}")

    # 3) Prepare transpile output folder (separate subfolder to avoid clobber)
    transpile_output_folder = Path(output_folder) / "transpiled" / timestamp
    _ensure_dir(str(transpile_output_folder))

    # Transpiler command:
    # databricks labs lakebridge transpile --source-dialect Synapse --input-source /path/to/input --output-folder /path/to/output
    transpile_cmd = [
        "databricks", "labs", "lakebridge", "transpile",
        "--source-dialect", "synapse",
        "--input-source", str(temp_dir),
        "--output-folder", str(transpile_output_folder)
    ]

    print("\nRunning Transpiler...")
    rc2, stdout2, stderr2 = _run_cmd(transpile_cmd)
    if rc2 != 0:
        print("\n[ERROR] Transpiler failed. See stderr above.")
        return {
            "success": False,
            "step": "transpile",
            "returncode": rc2,
            "stdout": stdout2,
            "stderr": stderr2,
            "transpile_output_folder": str(transpile_output_folder)
        }

    print(f"\nTranspiler finished successfully. Output folder: {transpile_output_folder}")

    # 4) Collect output file list
    transpiled_files = []
    for p in transpile_output_folder.rglob("*.sql"):
        transpiled_files.append(str(p))

    # 5) Return the result to Step 7
    result = {
        "success": True,
        "dialect": dialect,
        "temp_input_dir": str(temp_dir),
        "analyzer_report": str(analyzer_report),
        "transpile_output_folder": str(transpile_output_folder),
        "transpiled_files": transpiled_files
    }

    # Optionally, write a small manifest
    manifest_path = logs_dir / f"step6_manifest_{timestamp}.json"
    with open(manifest_path, "w", encoding="utf-8") as mf:
        json.dump(result, mf, indent=2)
    print(f"\nWrote manifest: {manifest_path}")

    print("\n============================================================")
    print("Core Engine (Step 6) Completed Successfully")
    print("============================================================")

    return result


if __name__ == "__main__":
    print("This module is intended to be invoked by main.py. Example usage:")
    print("  run_step6({'dialect':'synapse','processed_files':{'D:/.../pop.sql':'select 1'}, 'output_folder':'D:/lakebridge-accelerator/output/synapse'})")
