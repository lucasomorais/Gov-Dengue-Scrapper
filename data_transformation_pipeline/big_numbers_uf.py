import yaml, os, openpyxl, sys


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from modules.utils import (
    find_latest_file_in_subfolders,
    get_latest_epidemiology_file,
    OUTPUT_DIR,
    TEMP_DIR
)

def normalize_key(key: str) -> str:
    return (
        key.replace(" Do ", " do ")
           .replace(" De ", " de ")
           .strip()
           .lower()
    )

def big_numbers_uf():
    # === [1] Carrega YAML mais recente no padrão big_numbers_uf_*.yaml ===
    try:
        yaml_path = find_latest_file_in_subfolders('big_numbers_uf_*.yaml', output_dir=OUTPUT_DIR)
    except FileNotFoundError as e:
        print(f"[ERROR] YAML file not found: {e}")
        return

    with open(yaml_path, "r", encoding="utf-8") as f:
        yaml_data = yaml.safe_load(f)

    yaml_data_normalized = {
        normalize_key(k): v for k, v in yaml_data.items()
    }

    # === [2] Carrega planilha mais recente ===
    try:
        excel_path = get_latest_epidemiology_file(TEMP_DIR)
        wb = openpyxl.load_workbook(excel_path)
        ws = wb["Big Numbers UF"]
    except FileNotFoundError:
        print(f"[ERROR] Excel file not found in: {TEMP_DIR}")
        return
    except KeyError:
        print(f"[ERROR] Sheet 'Big Numbers UF' not found in {excel_path}")
        return

    # === [3] Mapeamento das colunas na planilha ===
    col_map = {
        'casos prováveis de dengue': 'G',
        'coeficiente de incidência': 'K',
        'óbitos em investigação': 'P',
        'óbitos por dengue': 'Q',
    }

    # === [4] Itera sobre os estados ===
    for row in ws.iter_rows(min_row=2):
        estado_nome = row[1].value.strip() if row[1].value else None  # Coluna B
        estado_normalizado = normalize_key(estado_nome) if estado_nome else None

        if not estado_normalizado or estado_normalizado not in yaml_data_normalized:
            continue

        dados_estado = yaml_data_normalized[estado_normalizado]
        for campo_yaml, valor in dados_estado.items():
            campo_normalizado = normalize_key(campo_yaml)
            for key_map, col_letter in col_map.items():
                if key_map in campo_normalizado:
                    if col_letter == 'G':
                        valor_limpo = int(str(valor).replace('.', '').replace(',', ''))
                        ws[f"{col_letter}{row[0].row}"] = valor_limpo
                    else:
                        try:
                            valor_convertido = float(str(valor).replace(',', '.'))
                            ws[f"{col_letter}{row[0].row}"] = valor_convertido
                        except ValueError:
                            print(f"[WARN] Valor inválido '{valor}' para {estado_nome} - {campo_yaml}")

    # === [5] Salva planilha modificada ===
    wb.save(excel_path)
    print(f"✅ Planilha atualizada: {excel_path}")

if __name__ == "__main__":
    big_numbers_uf()
