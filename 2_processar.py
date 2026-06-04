"""
Processamento dos dados brutos de reclamações da Localiza.
Lê reclamacoes_brutas.csv, limpa, categoriza e gera reclamacoes_processadas.csv.
"""

import os
import pandas as pd

# Caminhos dos arquivos
PASTA_DADOS = os.path.join(os.path.dirname(__file__), "dados")
ARQUIVO_ENTRADA = os.path.join(PASTA_DADOS, "reclamacoes_brutas.csv")
ARQUIVO_SAIDA   = os.path.join(PASTA_DADOS, "reclamacoes_processadas.csv")

# Mapeamento de nomes de estado por extenso para siglas
MAPA_ESTADOS = {
    "acre": "AC", "alagoas": "AL", "amapá": "AP", "amazonas": "AM",
    "bahia": "BA", "ceará": "CE", "distrito federal": "DF",
    "espírito santo": "ES", "goiás": "GO", "maranhão": "MA",
    "mato grosso": "MT", "mato grosso do sul": "MS", "minas gerais": "MG",
    "pará": "PA", "paraíba": "PB", "paraná": "PR", "pernambuco": "PE",
    "piauí": "PI", "rio de janeiro": "RJ", "rio grande do norte": "RN",
    "rio grande do sul": "RS", "rondônia": "RO", "roraima": "RR",
    "santa catarina": "SC", "são paulo": "SP", "sergipe": "SE",
    "tocantins": "TO",
}

# Palavras-chave por categoria (verificadas nesta ordem)
REGRAS_CATEGORIA = [
    (
        "Sinistro e Acidente",
        ["sinistro", "acidente", "colisão", "colidiu", "bateu", "batida",
         "indenização", "indenizar", "seguro", "avaria", "dano"],
    ),
    (
        "Problema Financeiro",
        ["caução", "estorno", "cobrança", "cartão", "débito",
         "reembolso", "cobrado", "desconto", "fatura", "dívida",
         "negativação", "serasa", "score", "parcela"],
    ),
    (
        "Bloqueio de Cadastro",
        ["cadastro bloqueado", "cadastro negado", "bloqueado", "bloqueio",
         "não consigo alugar", "negando", "sem justificativa", "restrição",
         "desbloqueio", "desbloquear"],
    ),
    (
        "Falha no App / Reserva",
        ["aplicativo", " app ", "reserva", "site", "sistema", "plataforma",
         "erro", "não carrega", "cancelar reserva", "alterar reserva",
         "confirmação", "não confirmou"],
    ),
    (
        "Multa e Infração",
        ["multa", "infração", "notificação", "detran", "autuação",
         "autuado", "indicação de condutor", "auto de infração"],
    ),
    (
        "Qualidade do Veículo",
        ["limpeza", "sujo", "cheiro", "arranhado", "amassado",
         "defeito", "pneu", "bateria", "freio", "motor",
         "ar-condicionado", "ar condicionado", "quebrado"],
    ),
    (
        "Tempo de Atendimento",
        ["atraso", "espera", "fila", "demora", "horas", "dias",
         "não apareceu", "cancelou", "lentidão", "prazo"],
    ),
    (
        "Falha no Atendimento",
        ["não resolveu", "ignorado", "sem resposta", "despreparado",
         "mal atendido", "grosseiro", "rude", "não respondeu",
         "sem retorno", "não entrou em contato"],
    ),
]


def padronizar_estado(valor):
    """
    Converte nome por extenso ou sigla para sigla oficial.
    Retorna 'Outros' se não reconhecido.
    """
    if not isinstance(valor, str) or not valor.strip():
        return "Outros"
    v = valor.strip().lower()
    # Já é uma sigla de dois caracteres
    if len(v) == 2 and v.upper() in MAPA_ESTADOS.values():
        return v.upper()
    # Busca pelo nome completo
    return MAPA_ESTADOS.get(v, "Outros")


def categorizar(texto):
    """
    Recebe o texto de preview de uma reclamação e retorna sua categoria.
    Verifica as regras na ordem definida em REGRAS_CATEGORIA.
    """
    if not isinstance(texto, str):
        return "Outros"
    texto_lower = texto.lower()
    for categoria, palavras in REGRAS_CATEGORIA:
        if any(palavra in texto_lower for palavra in palavras):
            return categoria
    return "Outros"


def limpar_dados(df):
    """
    Remove duplicatas, linhas sem título e a coluna 'data' (não coletada).
    Padroniza a coluna 'estado' para siglas oficiais.
    """
    print(f"Registros antes da limpeza: {len(df)}")
    df = df.drop_duplicates()
    df = df[df["titulo"].notna() & (df["titulo"].str.strip() != "")]
    df = df.drop(columns=["data"], errors="ignore")
    df["estado"] = df["estado"].apply(padronizar_estado)
    print(f"Registros após limpeza: {len(df)}")
    return df


def enriquecer_dados(df):
    """Classifica cada reclamação em uma categoria por palavras-chave."""
    df["categoria"] = df["texto_preview"].apply(categorizar)
    return df


def imprimir_resumo(df):
    """Imprime um resumo dos dados processados no terminal."""
    print(f"\n{'='*60}")
    print(f"Total de reclamações processadas: {len(df)}")

    print("\nContagem por categoria:")
    print(df["categoria"].value_counts().to_string())

    print("\nTop 10 estados com mais reclamações:")
    print(df["estado"].value_counts().head(10).to_string())
    print(f"{'='*60}\n")


def main():
    # Lê o arquivo bruto
    print(f"Lendo: {ARQUIVO_ENTRADA}")
    df = pd.read_csv(ARQUIVO_ENTRADA, encoding="utf-8-sig")

    df = limpar_dados(df)
    df = enriquecer_dados(df)
    df.to_csv(ARQUIVO_SAIDA, index=False, encoding="utf-8-sig")
    print(f"Arquivo salvo em: {ARQUIVO_SAIDA}")
    imprimir_resumo(df)


if __name__ == "__main__":
    main()
