# Análise de CX — Localiza no Reclame Aqui

Projeto de portfólio que coleta, processa e analisa reclamações públicas da Localiza
no Reclame Aqui para demonstrar habilidades em coleta de dados, SQL, NLP e visualização.

## Dashboard

[Acessar dashboard](https://localiza-cx-teste.streamlit.app/)

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

## Desafios enfrentados

O Reclame Aqui utiliza proteção Cloudflare contra automação, o que exigiu algumas adaptações durante a coleta.

A fase de listagem das reclamações (navegação entre páginas) funcionou sem bloqueios. O problema surgiu ao acessar as páginas individuais de cada reclamação em sequência — o volume de requisições consecutivas acionava verificações de bot periódicas, que precisavam ser resolvidas manualmente no navegador para que a coleta pudesse continuar.

Foram testadas alternativas como o Camoufox (Firefox modificado para parecer um usuário real) e a intercepção das chamadas de API internas do site. O Camoufox apresentou incompatibilidade com a versão do Node.js instalada. A análise das chamadas de rede revelou que os dados das reclamações são renderizados no servidor e não expostos via API, o que inviabilizou essa abordagem.

A solução adotada foi manter o navegador Chrome real com o script Playwright Stealth, aumentar os intervalos entre requisições e implementar pausas automáticas quando a verificação de bot era detectada. Com isso, foi possível coletar aproximadamente 500 reclamações por sessão — um volume representativo para análise, mas inferior ao total disponível no site.

## Arquivos

| Arquivo | Descrição |
|---|---|
| `1_scraper.py` | Coleta de dados via Playwright |
| `2_processar.py` | Limpeza, categorização e enriquecimento |
| `3_dashboard.py` | Dashboard interativo em Streamlit |
| `analise_sql.ipynb` | Análise complementar em SQL |

