import os
import sys
import yaml

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from modules.utils import find_latest_file_in_subfolders, OUTPUT_DIR

def normalize_key(key):
    return key.split(":")[0].strip().lower()

def parse_int(value):
    """Tenta converter string numérica com '.' como separador de milhar e ',' decimal para int."""
    if value is None:
        return 0
    try:
        return int(str(value).replace('.', '').replace(',', ''))
    except ValueError:
        return 0

def total_casos_provaveis_dengue(output_dir=OUTPUT_DIR):
    # Busca o arquivo YAML mais recente que começa com 'big_numbers_uf_'
    try:
        yaml_path = find_latest_file_in_subfolders('big_numbers_uf_*.yaml', output_dir=output_dir)
    except FileNotFoundError:
        print(f"[ERROR] Nenhum arquivo 'big_numbers_uf_*.yaml' encontrado em {output_dir} ou subpastas.")
        return 0

    with open(yaml_path, "r", encoding="utf-8") as f:
        yaml_data = yaml.safe_load(f)

    total_casos = 0
    target_key = "casos prováveis de dengue"

    for estado, dados in yaml_data.items():
        if not isinstance(dados, dict):
            continue
        for campo_yaml, valor in dados.items():
            if normalize_key(campo_yaml) == target_key:
                total_casos += parse_int(valor)
                break

    print(f"[INFO] Total de casos prováveis de dengue: {total_casos}")
    return total_casos

if __name__ == "__main__":
    total_casos_provaveis_dengue()
