# Análise de CX — Localiza no Reclame Aqui

Projeto de portfólio que coleta, processa e analisa reclamações públicas da Localiza
no Reclame Aqui para demonstrar habilidades em coleta de dados, SQL, NLP e visualização.

## Stack

Python, Playwright, Pandas, SQL (SQLite), Streamlit e Plotly.

## Pipeline

**Coleta:** scraper em Playwright que navega pelas páginas de reclamações da Localiza
e extrai título, status, localização, texto e nota do cliente.

**Processamento:** limpeza e padronização com Pandas, categorização por palavras-chave
em oito categorias operacionais e criação de métricas de análise.

**Análise SQL:** notebook Jupyter com consultas SQL sobre uma base SQLite em memória,
respondendo perguntas de negócio sobre resolução, satisfação e padrões regionais.

**Dashboard:** aplicação Streamlit com filtros interativos, métricas de CX,
gráficos por categoria e estado, e análise de desempenho regional.

## Como executar localmente

```bash
pip install -r requirements.txt
playwright install chromium
python 1_scraper.py
python 2_processar.py
streamlit run 3_dashboard.py
```

## Principais insights

- 44,9% das reclamações são financeiras, com taxa de resolução de 43,8%
- Bloqueio de Cadastro tem a menor taxa de resolução (14,3%) e a pior nota média (3,54)
- Reclamações resolvidas têm nota 8,79; não resolvidas têm nota 1,11
- Minas Gerais performa acima da média nacional, com exceção da categoria Sinistro e Acidente
- 46,2% das reclamações de Belo Horizonte não receberam nenhuma resposta

## Arquivos

| Arquivo | Descrição |
|---|---|
| `1_scraper.py` | Coleta de dados via Playwright |
| `2_processar.py` | Limpeza, categorização e enriquecimento |
| `3_dashboard.py` | Dashboard interativo em Streamlit |
| `analise_sql.ipynb` | Análise complementar em SQL |

## Autor

[Seu nome]
[Link do LinkedIn]
