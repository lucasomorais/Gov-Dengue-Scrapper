import os
import subprocess
import sys
from datetime import datetime

def log_info(message):
    """Log messages with timestamp in the required [INFO] format."""
    print(f"[INFO] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}")

def main():
    total_start_time = datetime.now()
    current_date = datetime.now().strftime("%m-%d-%y")

    folders = [
        "Big_Numbers_UF/output",
        "SE_COMPLETA_2023-24/output",
        "Informe_Semana_Epidemiologica/output",
        "_results",
        "_results/_final_output",
        "_results/Informe_Semana_Epidemiologica_DATA/",
        "_results/SE_COMPLETA_2023-24_DATA/",
        "_results/City_Cases_2024_DATA",
        "_results/Big_Numbers_DATA/",
        "Informe_Semana_Epidemiologica/copy",
        "Dengue_Cases_Year",
        "_results/Dengue_Cases_Year_DATA"  # Added new output folder
    ]

    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        log_info(f"Ensured folder exists: {folder}")

    scripts = [
        ("Big_Numbers_UF/uf_data.py", "Big_Numbers_UF/output/dengue_uf_data.yaml"),
        ("Big_Numbers_UF/yaml_to_excel.py", f"_results/Big_Numbers_DATA/Big_Numbers_UF_{current_date}.xlsx"),
        ("Dengue_Cases_Year/Dengue_Cases_Year.py", f"_results/Dengue_Cases_Year_DATA/Dengue_Cases_Year_{current_date}.xlsx"),  # Updated output
        ("SE_COMPLETA_2023-24/table_data.py", "SE_COMPLETA_2023-24/output/SE_COMPLETA_2023-24.csv"),
        ("SE_COMPLETA_2023-24/csv_to_excel.py", f"_results/SE_COMPLETA_2023-24_DATA/SE_COMPLETA_2023-24_{current_date}.xlsx"),
        ("City_Cases-2024/City_Cases_2024.py", f"_results/City_Cases_2024_DATA/City_Cases_{current_date}.xlsx"),
        ("Informe_Semana_Epidemiologica/SE_fetcher.py", "Informe_Semana_Epidemiologica/output/SE-Y.yaml"),
        ("Informe_Semana_Epidemiologica/transforming_into_SE.py", f"_results/Informe_Semana_Epidemiologica_DATA/Informe_Semana_Epidemiologica_{current_date}.xlsx"),
        ("_results/_group_sheets.py", f"_results/_final_output/Epidemiology_Dengue_{current_date}.xlsx")
    ]

    for script, output_file in scripts:
        log_info(f"Starting {script}")
        start_time = datetime.now()
        try:
            subprocess.run([sys.executable, script], check=True)
        except subprocess.CalledProcessError as e:
            log_info(f"Error in {script}: {e}")
            sys.exit(1)
        if not os.path.exists(output_file):
            log_info(f"Error: Output file {output_file} not found after running {script}")
            sys.exit(1)
        duration = datetime.now() - start_time
        log_info(f"Finished {script}")
        log_info(f"{script} took {duration.total_seconds()} seconds")

    total_duration = datetime.now() - total_start_time
    log_info(f"Total execution time: {total_duration.total_seconds()} seconds")
    log_info("All scripts completed successfully.")

if __name__ == "__main__":
    main()