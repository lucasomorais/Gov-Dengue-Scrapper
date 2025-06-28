import os
import glob
import pandas as pd

def city_cases_formatter():
    try:
        # === [1] Setup paths ===
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)

        # Encontra o CSV mais recente no padrão output/dengue_*/city_cases_*.csv
        search_pattern = os.path.join(project_root, "output", "dengue_*", "city_cases_*.csv")
        csv_files = glob.glob(search_pattern)

        if not csv_files:
            raise FileNotFoundError("Nenhum arquivo 'city_cases_*.csv' encontrado em output/dengue_*/")

        latest_csv = max(csv_files, key=os.path.getmtime)
        print(f"[INFO] Usando arquivo mais recente: {latest_csv}")

        # Extrai timestamp do nome do arquivo
        timestamp = os.path.basename(latest_csv).replace("city_cases_", "").replace(".csv", "")
        output_dir = os.path.dirname(latest_csv)

        # === [2] Processa CSV original ===
        df = pd.read_csv(latest_csv, skiprows=3, sep=';', encoding='latin1', quotechar='"')

        df['Cod Mun'] = df['Município de residência'].str[:6]
        df['Nome Mun'] = df['Município de residência'].str[7:].str.strip()
        df = df[['Cod Mun', 'Nome Mun', 'Casos_Prováveis']]
        df.columns = ['Cod Mun', 'Nome Mun', 'Casos Provaveis']
        df = df[df['Cod Mun'].str.match(r'^\d{6}$') & (df['Cod Mun'] != '000000')]

        # === [3] Salva arquivo processado com mesmo nome, mas reescreve limpo ===
        final_output_path = os.path.join(output_dir, f"city_cases_{timestamp}.csv")
        df.to_csv(final_output_path, index=False, encoding='utf-8-sig')

        print(f"[SUCCESS] Processed file saved as: {final_output_path}")

    except Exception as e:
        print(f"[ERROR] Failed to process city_cases CSV: {e}")
        raise

if __name__ == "__main__":
    city_cases_formatter()
