import os
import pandas as pd
from datetime import datetime

def main():
    try:
        # Setup paths and timestamp
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        output_dir = os.path.join(project_root, "output")
        timestamp = datetime.now().strftime("%Y_%m_%d")
        original_path = os.path.join(output_dir, f"city_cases_{timestamp}.csv")

        # Read the CSV, skip the first 4 rows, use semicolon delimiter, and specify encoding
        df = pd.read_csv(original_path, skiprows=0, sep=';', header=None, encoding='latin1')

        # Split Column 0 into two columns: code and name
        df['code'] = df[0].str[:6]  # First 6 characters for the code
        df['name'] = df[0].str[7:].str.strip()  # The rest, after the space, for the name

        # Keep only the desired columns: code, name, and Casos_Prováveis
        df = df[['code', 'name', 1]]
        df.columns = ['Cod Mun', 'Nome Mun', 'Casos Provaveis']

        # Filter out footer rows: keep only rows where 'code' is a 6-digit number and not '000000'
        df = df[df['Cod Mun'].str.match(r'^\d{6}$') & (df['Cod Mun'] != '000000')]

        # Define the fixed output file path relative to the project root
        output_file = f"output/city_cases_{timestamp}.csv"
        final_output_path = os.path.join(project_root, output_file)

        # Ensure the target directory exists
        os.makedirs(os.path.dirname(final_output_path), exist_ok=True)

        # Save to Excel
        df.to_csv(final_output_path, index=False, encoding='utf-8-sig')

        print(f"[SUCCESS] Processed file saved as: {final_output_path}")

    except Exception as e:
        print(f"[ERROR] Failed to process city_cases CSV: {e}")
        raise

if __name__ == "__main__":
    main()
