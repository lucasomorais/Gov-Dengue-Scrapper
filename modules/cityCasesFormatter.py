import os
import pandas as pd
from datetime import datetime

def city_cases_formatter():
    try:
        # Setup paths and timestamp
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        timestamp = datetime.now().strftime("%Y_%m_%d")
        output_dir = os.path.join(project_root, f"output/dengue_{timestamp}/")
        original_path = os.path.join(output_dir, f"city_cases_{timestamp}.csv")

        # Read CSV with header on the 4th line (after skipping 3), semicolon separator, latin1 encoding
        df = pd.read_csv(original_path, skiprows=3, sep=';', encoding='latin1', quotechar='"')

        # Split "Município de residência" into 'Cod Mun' and 'Nome Mun'
        df['Cod Mun'] = df['Município de residência'].str[:6]
        df['Nome Mun'] = df['Município de residência'].str[7:].str.strip()

        # Keep only necessary columns
        df = df[['Cod Mun', 'Nome Mun', 'Casos_Prováveis']]
        df.columns = ['Cod Mun', 'Nome Mun', 'Casos Provaveis']

        # Filter valid municipal codes (6-digit and not '000000')
        df = df[df['Cod Mun'].str.match(r'^\d{6}$') & (df['Cod Mun'] != '000000')]

        # Define output path and ensure directory exists
        # Define output path in dated folder and ensure directory exists
        dated_output_dir = os.path.join(project_root, f"output/dengue_{timestamp}")
        os.makedirs(dated_output_dir, exist_ok=True)
        final_output_path = os.path.join(dated_output_dir, f"city_cases_{timestamp}.csv")
        os.makedirs(os.path.dirname(final_output_path), exist_ok=True)

        # Save as UTF-8 CSV
        df.to_csv(final_output_path, index=False, encoding='utf-8-sig')
        print(f"[SUCCESS] Processed file saved as: {final_output_path}")

    except Exception as e:
        print(f"[ERROR] Failed to process city_cases CSV: {e}")
        raise

city_cases_formatter()
