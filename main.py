import time
import subprocess
from pathlib import Path
from datetime import datetime

from modules.utils import (
    ensure_directories_exist,
    get_latest_epidemiology_file,
    copy_latest_file_to_temp,
    SOURCE_DIR,
)
from modules.cityCasesFormatter import city_cases_formatter

from data_transformation_pipeline.informe_semana_epidemiologica import informe_semana_epidemiologica
from data_transformation_pipeline.big_numbers_uf import big_numbers_uf
from data_transformation_pipeline.se_completa import se_completa
from data_transformation_pipeline.update_city_cases import update_city_cases
from data_transformation_pipeline.dengue_cases_year import dengue_cases_year


def main():
    start = time.time()
    print(f"[START] Data pipeline started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Run the JS pipeline
    base_dir = Path(__file__).resolve().parent
    js_file_path = (base_dir / "data_fetching_pipeline" / "main.js").resolve()

    try:
        subprocess.run(["node", str(js_file_path)], check=True)
        print("[INFO] JavaScript pipeline executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] JavaScript pipeline failed: {e}")
        return

    # Utility steps
    city_cases_formatter()
    ensure_directories_exist()
    get_latest_epidemiology_file(SOURCE_DIR)
    copy_latest_file_to_temp()

    # ETL steps
    informe_semana_epidemiologica()
    big_numbers_uf()
    se_completa()
    update_city_cases()
    dengue_cases_year()

    end = time.time()
    elapsed = end - start
    print(f"[END] Pipeline completed in {elapsed:.2f} seconds at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
