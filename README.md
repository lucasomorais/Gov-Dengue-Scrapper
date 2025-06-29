# 🕸️ Dash Gerencial: Dengue Data ETL Pipeline

A robust end-to-end pipeline that collects, processes, validates, and structures epidemiological dengue data from Brazilian public sources, including Power BI dashboards and Tabnet (Datasus).

The pipeline is built in two main stages:

1. **Data Fetching (Node.js + Playwright)**
2. **Data Transformation (Python + openpyxl)**

All outputs are validated by automated tests and only moved to the final destination if they pass.

---

## 🔗 Data Sources

* [Datasus Tabnet](http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sinannet/cnv/denguebbr.def)
* Ministério da Saúde Power BI Panel (for SE, UF, and case metrics)

---

## 📦 Project Structure

```
├── data_fetching_pipeline/          # Web scraping (Playwright in Node.js)
│   ├── main.js                      # Orchestrates the scraping steps
│   ├── cityCases.js                # Scrapes city-level dengue data (CSV)
│   ├── bigNumbersUF.js            # Scrapes state-level metrics (YAML)
│   ├── SEFetcher.js                # Scrapes latest epidemiological week (YAML)
│   ├── semanaEpidemiologica.js    # Scrapes week-by-week data (CSV-like YAML)
│   └── utils.js                    # Shared scraping utilities
│
├── data_transformation_pipeline/   # ETL scripts (Python)
│   ├── informe_semana_epidemiologica.py
│   ├── big_numbers_uf.py
│   ├── se_completa.py
│   ├── update_city_cases.py
│   ├── dengue_cases_year.py
│
├── test/                           # Automated validations
│   └── test.py                     # Pytest suite to validate output files
│
├── modules/                        # Shared Python utils
│   └── utils.py
│
├── output/                         # Final validated outputs (CSV, YAML)
├── temp/                           # Temporary files pre-validation
├── main.py                         # Entrypoint for full ETL + test + deploy
└── README.md
```

---

## 🚀 How It Works

### 1. Data Fetching (Node.js)

The pipeline uses Playwright (headless browser automation) to simulate user behavior and extract data from dynamic dashboards.

Each scraping script is responsible for a different data scope:

* **`cityCases.js`**: Downloads CSV with city-level dengue counts.
* **`bigNumbersUF.js`**: Extracts state-level totals (cases, deaths, incidence).
* **`SEFetcher.js`**: Finds and exports latest epidemiological week metrics.
* **`semanaEpidemiologica.js`**: Scrapes weekly data across all UFs.

Files are saved to the `output/` folder, timestamped as `dengue_YYYY_MM_DD`.

---

### 2. Data Transformation (Python)

The ETL phase loads the raw YAML and CSV files, applies formatting, transformations, validation, and updates an Excel spreadsheet (`Epidemiology_Dengue_YYYY_MM_DD.xlsx`) structured in multiple sheets:

* **City Cases**: Aggregated city-level dengue cases
* **Big Numbers UF**: State-level metrics
* **SE Completa**: Weekly case breakdowns
* **Informe Semana Epidemiológica**: Summary of the most recent week
* **Dengue Cases Year**: Yearly aggregation by state

---

### 3. Validation (pytest)

After data is processed, a test suite (`test/test.py`) runs to validate:

* Structural integrity of Excel sheets
* Consistency between YAML/CSV sources and Excel content
* Completeness of epidemiological weeks

> 📌 Only if **all tests pass**, the output files are moved from `temp/` to `output/`. This avoids promoting invalid data.

---

## 🧪 Tests Overview

* `test_update_city_cases`: Validates alignment between CSV and Excel's City Cases sheet
* `test_big_numbers_uf`: Checks if Excel matches the YAML state-level metrics
* `test_se_completa`: Verifies completeness and correctness of week-level data
* `test_informe_semana_epidemiologica`: Compares latest week in Excel with YAML
* `test_dengue_cases_year`: Asserts yearly aggregation from state-level inputs
* `test_move_file`: Ensures file move happens only when tests succeed

Run them manually with:

```bash
pytest test/test.py -v
```

Or automatically via the pipeline (`main.py`).

---

## 🧰 Requirements

* Node.js (Playwright)
* Python 3.9+
* Dependencies:

  * `playwright`, `pandas`, `openpyxl`, `pytest`, `pyyaml`

---

## ▶️ Running the Full Pipeline

From project root:

```bash
python main.py
```

This will:

1. Run all Playwright scraping steps
2. Format and transform the data
3. Generate Excel output
4. Validate output with tests
5. Move final files only if all tests pass


### pip install -r requirements.txt

Dont forget about the playwright install, also i dont know if the requirements is correctly grabbing Node requirements
if it is not grabbing correctly, use:

npm init -y
npm install playwright js-yaml