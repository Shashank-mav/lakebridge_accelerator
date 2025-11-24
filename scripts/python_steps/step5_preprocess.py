import os
import importlib.util
import yaml
from pathlib import Path

def load_module(path):
    spec = importlib.util.spec_from_file_location("module", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def run_step5(dummy_input=None):
    print("============================================================")
    print("Lakebridge Accelerator - Pre-process (Step 5)")
    print("============================================================")

    root_dir = Path(__file__).resolve().parents[2]
    config_path = root_dir / "config" / "config.yaml"

    if not config_path.exists():
        print(f"ERROR: Config file not found: {config_path}")
        return None

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    dialect = config.get("dialect", "synapse").lower().replace(" ", "_")
    input_root = Path(config.get("source_path", str(root_dir / "input")))
    output_root = Path(config.get("target_path", str(root_dir / "output")))

    dialect_input_folder = input_root / dialect
    dialect_output_folder = output_root / dialect

    if not dialect_input_folder.exists():
        print(f"ERROR: Dialect input folder not found: {dialect_input_folder}")
        return None

    files = sorted([p for p in dialect_input_folder.glob("*.sql") if p.is_file()])

    if not files:
        print(f"ERROR: No SQL files found in: {dialect_input_folder}")
        return None

    print(f"Dialect: {dialect}")
    print(f"Input folder: {dialect_input_folder}")
    print(f"Output folder: {dialect_output_folder}")
    print(f"Files detected: {[f.name for f in files]}")

    preprocessor_path = root_dir / "dialects" / dialect / "preprocessor" / "preprocess.py"

    if not preprocessor_path.exists():
        print(f"ERROR: Preprocessor not found: {preprocessor_path}")
        return None

    print(f"Using preprocessor: {preprocessor_path}")
    pre_mod = load_module(str(preprocessor_path))

    processed_files = {}
    for file in files:
        print(f"\nPreprocessing file: {file.name}")
        with open(file, "r", encoding="utf-8") as fh:
            sql_text = fh.read()
        processed_sql = pre_mod.preprocess(sql_text)
        processed_files[str(file.resolve())] = processed_sql

    print("\n============================================================")
    print("Pre-process Completed (Step 5)")
    print("============================================================")

    return {
        "dialect": dialect,
        "processed_files": processed_files,
        "output_folder": str(dialect_output_folder)
    }

if __name__ == "__main__":
    print("This module is intended to be called from main.py")
