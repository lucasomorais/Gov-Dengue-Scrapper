import yaml

def normalize_key(key):
    return key.split(":")[0].strip().lower()

def parse_int(value):
    """Tenta converter string numérica com '.' como separador de milhar e ',' decimal para int."""
    if value is None:
        return 0
    try:
        # Remove pontos e vírgulas, tenta converter para inteiro
        return int(str(value).replace('.', '').replace(',', ''))
    except ValueError:
        # Se não conseguir converter, retorna 0 ou levanta erro, dependendo da sua escolha
        return 0

def main():
    yaml_file = "output/big_numbers_uf_2025_06_27.yaml"

    with open(yaml_file, "r", encoding="utf-8") as f:
        yaml_data = yaml.safe_load(f)

    total_casos = 0
    target_key = "casos prováveis de dengue"

    for estado, dados in yaml_data.items():
        if not isinstance(dados, dict):
            continue  # Segurança: pula se dados não for dict

        # Procura o campo 'casos prováveis de dengue' dentro do dict do estado
        for campo_yaml, valor in dados.items():
            if normalize_key(campo_yaml) == target_key:
                total_casos += parse_int(valor)
                break  # achou o campo, pode sair do loop do estado

    print(f"Total de casos prováveis de dengue: {total_casos}")

if __name__ == "__main__":
    main()
