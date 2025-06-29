import time, subprocess
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

    base_dir = Path(__file__).resolve().parent

    # 1. Run JS scraping
    js_file_path = (base_dir / "data_fetching_pipeline" / "main.js").resolve()
    try:
        subprocess.run(["node", str(js_file_path)], check=True)
        print("[INFO] JavaScript pipeline executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] JavaScript pipeline failed: {e}")
        return

    # 2. Prepare data
    city_cases_formatter()
    ensure_directories_exist()
    get_latest_epidemiology_file(SOURCE_DIR)
    copy_latest_file_to_temp()

    # 3. Transform data
    informe_semana_epidemiologica()
    big_numbers_uf()
    se_completa()
    update_city_cases()
    dengue_cases_year()

    # 4. TESTS
    print("[INFO] Running validation tests...")
    test_result = subprocess.run(["pytest", "test/test.py", "-v"], cwd=base_dir)

    if test_result.returncode != 0:
        print("[ERROR] Some tests failed. Review logs above. Output files will remain in TEMP.")
        return
    else:
        print("[SUCCESS] All tests passed. Pipeline is valid and complete.")

    end = time.time()
    elapsed = end - start
    print(f"[END] Pipeline completed in {elapsed:.2f} seconds at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
