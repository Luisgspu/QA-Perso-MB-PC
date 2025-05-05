import shutil
import os

def copy_categories_json(report_dir):
    # Path to the categories.json file
    categories_file = "path/to/categories.json"  # Replace with the actual path to your categories.json file

    # Ensure the report directory exists
    if not os.path.exists(report_dir):
        raise FileNotFoundError(f"Report directory does not exist: {report_dir}")

    # Copy categories.json to the report directory
    shutil.copy(categories_file, os.path.join(report_dir, "categories.json"))
    print(f"✅ categories.json copied to {report_dir}")