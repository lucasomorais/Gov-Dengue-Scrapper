import os
import subprocess
import sys
from datetime import datetime

def log_info(message):
    """Log messages with timestamp in the required [INFO] format."""
    print(f"[INFO] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}")

def main():
    # Record the start time of the entire process
    total_start_time = datetime.now()

    # List of folders required by the scripts
    folders = [
        "Big_Numbers_UF/output",           # For uf_data.py output
        "SE_COMPLETA_2023-24/output",      # For table_data.py output
        "Semana_Epidemiologica/output",    # For SE_fetcher.py output
        "results",                         # For yaml_to_excel.py and csv_to_excel.py outputs
        "Semana_Epidemiologica/copy-to-test"  # For transforming_into_SE.py input and output
    ]

    # Ensure all necessary folders exist
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        log_info(f"Ensured folder exists: {folder}")

    # Define the scripts and their expected output files in execution order
    scripts = [
        ("uf_data.py", "Big_Numbers_UF/output/dengue_uf_data.yaml"),
        ("yaml_to_excel.py", "results/Big_Numbers_UF.xlsx"),
        ("table_data.py", "SE_COMPLETA_2023-24/output/SE_COMPLETA_2023-24.csv"),
        ("csv_to_excel.py", "results/SE_COMPLETA_2023-24.xlsx"),
        ("SE_fetcher.py", "Semana_Epidemiologica/output/SE-Y.yaml"),
        ("transforming_into_SE.py", "Semana_Epidemiologica/copy-to-test/Epidemiology - Dengue_updated.xlsx")
    ]

    # Run each script in sequence
    for script, output_file in scripts:
        log_info(f"Starting {script}")
        start_time = datetime.now()

        # Execute the script using the current Python interpreter
        try:
            subprocess.run([sys.executable, script], check=True)
        except subprocess.CalledProcessError as e:
            log_info(f"Error in {script}: {e}")
            sys.exit(1)

        # Verify that the expected output file was created
        if not os.path.exists(output_file):
            log_info(f"Error: Output file {output_file} not found after running {script}")
            sys.exit(1)

        # Calculate and log the duration
        duration = datetime.now() - start_time
        log_info(f"Finished {script}")
        log_info(f"{script} took {duration.total_seconds()} seconds")

    # Calculate and log the total execution time
    total_duration = datetime.now() - total_start_time
    log_info(f"Total execution time: {total_duration.total_seconds()} seconds")
    log_info("All scripts completed successfully.")

if __name__ == "__main__":
    main()