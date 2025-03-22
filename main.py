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

    # Calculate current date once for consistency across all scripts
    current_date = datetime.now().strftime("%m-%d-%y")

    # List of folders required by the scripts
    folders = [
        "Big_Numbers_UF/output",
        "SE_COMPLETA_2023-24/output",
        "Informe_Semana_Epidemiologica/output",
        "City_Cases-2024/output",

        "_results",
        "_results/_final_output",
        "_results/Informe_Semana_Epidemiologica_DATA/",
        "_results/SE_COMPLETA_2023-24_DATA/",
        "_results/City_Cases_2024_DATA",
        "_results/Big_Numbers_DATA/",
        "Informe_Semana_Epidemiologica/copy"
    ]

    # Ensure all necessary folders exist
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        log_info(f"Ensured folder exists: {folder}")

    # Define the scripts and their expected output files in execution order
    scripts = [
        #("Big_Numbers_UF/uf_data.py", "Big_Numbers_UF/output/dengue_uf_data.yaml"),
        #("Big_Numbers_UF/yaml_to_excel.py", f"_results/Big_Numbers_DATA/Big_Numbers_UF_{current_date}.xlsx"),
        #("SE_COMPLETA_2023-24/table_data.py", "SE_COMPLETA_2023-24/output/SE_COMPLETA_2023-24.csv"),
        #("SE_COMPLETA_2023-24/csv_to_excel.py", f"_results/SE_COMPLETA_2023-24_DATA/SE_COMPLETA_2023-24_{current_date}.xlsx"),
        #("City_Cases-2024/City_Cases_2024.py", f"_results/City_Cases_2024_DATA/City_Cases_{current_date}.xlsx"),
        #("Informe_Semana_Epidemiologica/SE_fetcher.py", "Informe_Semana_Epidemiologica/output/SE-Y.yaml"),
        ("Informe_Semana_Epidemiologica/transforming_into_SE.py", f"_results/Informe_Semana_Epidemiologica_DATA/Informe_Semana_Epidemiologica_{current_date}.xlsx"),
        ("_results/_group_sheets.py", f"_results/_final_output/Epidemiology_Dengue_{current_date}.xlsx")
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