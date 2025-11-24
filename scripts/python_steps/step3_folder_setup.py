import os

def create_folder(path: str):
    """Creates a folder if it does not exist."""
    try:
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Created: {path}")
        else:
            print(f"Exists:  {path}")
    except Exception as e:
        print(f"ERROR creating folder {path}: {e}")


def run_step3():
    print("============================================================")
    print("Lakebridge Accelerator - Folder Setup (Step 3)")
    print("============================================================")

    # Step 3 script resides in:
    # D:/lakebridge-accelerator/scripts/python_steps/
    # → root is two levels up
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, "..", ".."))

    print(f"Root Directory Detected: {root_dir}\n")

    folders_to_create = [
        f"{root_dir}/input",
        f"{root_dir}/input/synapse",

        f"{root_dir}/output",
        f"{root_dir}/output/synapse",

        f"{root_dir}/dialects",
        f"{root_dir}/dialects/synapse",
        f"{root_dir}/dialects/snowflake",
        f"{root_dir}/dialects/oracle",
        f"{root_dir}/dialects/teradata",
        f"{root_dir}/dialects/sqlserver",
        f"{root_dir}/dialects/generic",

        f"{root_dir}/temp",
        f"{root_dir}/logs"
    ]

    for folder in folders_to_create:
        create_folder(folder)

    print("\n============================================================")
    print("Folder Structure Setup Completed Successfully (Step 3)")
    print("============================================================")


if __name__ == "__main__":
    run_step3()
