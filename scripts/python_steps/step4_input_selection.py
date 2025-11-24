import os

def run_step4():
    print("============================================================")
    print("Lakebridge Accelerator - Input Selection (Step 4)")
    print("============================================================")

    # Detect root = two levels up from this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, "..", ".."))

    print(f"Root Directory: {root_dir}\n")

    # ---------------------------------------------------------
    # 1. Ask user dialect
    # ---------------------------------------------------------
    print("Available Dialects:")
    dialects = ["synapse"]  # expand later
    for idx, d in enumerate(dialects, 1):
        print(f"  {idx}. {d}")

    choice = input("\nSelect dialect number: ").strip()
    try:
        choice = int(choice)
        if choice < 1 or choice > len(dialects):
            raise ValueError()
    except:
        print("Invalid choice. Exiting step.")
        return

    dialect = dialects[choice - 1]
    print(f"\nSelected Dialect: {dialect}")

    # ---------------------------------------------------------
    # 2. Scan input folder for selected dialect
    # ---------------------------------------------------------
    input_folder = os.path.join(root_dir, "input", dialect)

    if not os.path.exists(input_folder):
        print(f"ERROR: Input folder not found: {input_folder}")
        return

    files = [f for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f))]

    if not files:
        print(f"No files found in {input_folder}")
        return

    print(f"\nFiles found in {input_folder}:")
    for f in files:
        print(f"  - {f}")

    # ---------------------------------------------------------
    # 3. Ask user: All files or specific?
    # ---------------------------------------------------------
    run_mode = input("\nRun ALL files? (y/n): ").strip().lower()

    if run_mode == "y":
        selected_files = files
        print("\nSelected: ALL files")
    else:
        filename = input("Enter EXACT filename to run: ").strip()
        if filename not in files:
            print(f"ERROR: File '{filename}' not found in input folder.")
            return
        selected_files = [filename]
        print(f"\nSelected File: {filename}")

    # ---------------------------------------------------------
    # 4. Confirm output destination
    # ---------------------------------------------------------
    output_folder = os.path.join(root_dir, "output", dialect)
    print(f"\nOutput will be generated in:\n{output_folder}")

    confirm = input("\nProceed with this output location? (y/n): ").strip().lower()
    if confirm != "y":
        print("Cancelled by user.")
        return

    # ---------------------------------------------------------
    # 5. Return selected file paths for next step
    # ---------------------------------------------------------
    selected_full_paths = [os.path.join(input_folder, f) for f in selected_files]

    print("\n============================================================")
    print("Input Selection Completed (Step 4)")
    print("============================================================")

    # returned to Step 5 (pre-process)
    return {
        "dialect": dialect,
        "input_folder": input_folder,
        "output_folder": output_folder,
        "files": selected_full_paths
    }


if __name__ == "__main__":
    result = run_step4()
    print("\nReturned Data:")
    print(result)
