"""
Scraper de reclamações da Localiza no Reclame Aqui.
Coleta reclamações em três passagens por status.
Para cada reclamação acessa a página individual para obter
texto completo, cidade, estado e nota do cliente.
"""

import time
import random
import csv
import os
import re
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

# URL base da empresa no Reclame Aqui
BASE_URL = "https://www.reclameaqui.com.br/empresa/localiza-aluguel-de-carros/lista-reclamacoes/"

# Pasta de saída
PASTA_DADOS = os.path.join(os.path.dirname(__file__), "dados")
ARQUIVO_SAIDA = os.path.join(PASTA_DADOS, "reclamacoes_brutas.csv")

# Número máximo de páginas por passagem
MAX_PAGINAS = 50

# Status a coletar e seus parâmetros de URL
STATUS_PASSAGENS = [
    {"label": "Respondidas",     "status": "REPLIED"},
    {"label": "Não Respondidas", "status": "NOT_REPLIED"},
    {"label": "Avaliadas",       "status": "EVALUATED"},
]


def esperar():
    """Aguarda um intervalo aleatório entre 3 e 5 segundos."""
    time.sleep(random.uniform(3, 5))


def construir_url(status_param, pagina):
    """Monta a URL de listagem com filtro de status e número de página."""
    return f"{BASE_URL}?status={status_param}&pagina={pagina}"


def esta_em_bot_check(page):
    """Retorna True se a página atual é uma tela de verificação de bot."""
    indicadores = [
        "verificando se você é humano",
        "checking if the site connection is secure",
        "just a moment",
        "cf-browser-verification",
        "challenge-form",
        "enable javascript and cookies",
    ]
    try:
        conteudo = page.content().lower()
        return any(ind in conteudo for ind in indicadores)
    except Exception:
        return False


def aguardar_se_bot(page):
    """
    Detecta bot check e pausa para resolução manual.
    Após o ENTER, aguarda a página estabilizar completamente
    antes de retornar — evita o problema de navegação pendente.
    """
    if not esta_em_bot_check(page):
        return

    print("\n" + "!" * 60)
    print("  VERIFICAÇÃO DE BOT DETECTADA!")
    print("  1. Resolva o desafio no Chrome")
    print("  2. Aguarde a página carregar completamente")
    print("  3. Pressione ENTER aqui para continuar...")
    print("!" * 60)
    input()

    # Aguarda todas as navegações pendentes terminarem
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        pass
    time.sleep(3)

    # Se ainda estiver em bot check, pede de novo
    if esta_em_bot_check(page):
        print("  Ainda em verificação. Resolva e pressione ENTER novamente...")
        input()
        try:
            page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        time.sleep(3)


def navegar_com_retry(page, url, tentativas=3):
    """
    Navega para uma URL com retry em caso de erro de navegação interrompida.
    Retorna True se conseguiu, False se falhou todas as tentativas.
    """
    for i in range(tentativas):
        try:
            page.goto(url, timeout=30000, wait_until="domcontentloaded")
            return True
        except Exception as e:
            erro = str(e).lower()
            if "interrupted" in erro:
                # Navegação interrompida — aguarda estabilizar e tenta de novo
                print(f"  [retry] Navegação interrompida, aguardando 5s (tentativa {i+1}/{tentativas})...")
                time.sleep(5)
                try:
                    page.wait_for_load_state("networkidle", timeout=10000)
                except Exception:
                    pass
            else:
                print(f"  [erro] {e}")
                return False
    return False


def extrair_links_pagina(page):
    """
    Extrai os links e status de cada card na página de listagem.
    """
    resultados = []

    try:
        page.wait_for_selector("article.complaint-listagem-v2-card", timeout=15000)
    except Exception:
        try:
            page.wait_for_selector("article", timeout=10000)
        except Exception:
            return resultados

    itens = page.query_selector_all("article.complaint-listagem-v2-card")
    if not itens:
        itens = page.query_selector_all("article")

    for item in itens:
        try:
            link_el = item.query_selector("a")
            href = link_el.get_attribute("href") if link_el else ""
            if href and not href.startswith("http"):
                href = "https://www.reclameaqui.com.br" + href

            span_el = item.query_selector("span")
            status = span_el.inner_text().strip() if span_el else ""

            if href:
                resultados.append({"link": href, "status": status})
        except Exception:
            continue

    return resultados


def extrair_pagina_individual(page, link, status_card):
    """
    Acessa a página individual de uma reclamação e extrai todos os campos.
    """
    dados = {
        "titulo": "",
        "data": "",
        "status": status_card,
        "cidade": "",
        "estado": "",
        "texto_preview": "",
        "link": link,
        "nota_cliente": "",
    }

    ok = navegar_com_retry(page, link)
    if not ok:
        return dados

    esperar()
    aguardar_se_bot(page)

    try:
        titulo_el = page.query_selector("h1")
        if titulo_el:
            dados["titulo"] = titulo_el.inner_text().strip()

        data_el = page.query_selector("time")
        if data_el:
            dados["data"] = (
                data_el.get_attribute("datetime") or data_el.inner_text().strip()
            )

        texto_el = page.query_selector(
            "[class*='complaint-body'], [class*='complaintBody'], "
            "[class*='description'], [data-testid*='complaint-body']"
        )
        if not texto_el:
            for p in page.query_selector_all("p"):
                t = p.inner_text().strip()
                if len(t) > 80:
                    texto_el = p
                    break
        if texto_el:
            dados["texto_preview"] = texto_el.inner_text().strip()

        # Cidade e estado extraídos do JSON embutido na página
        # Formato: {"key":"city","value":"..."}, {"key":"state","value":"..."}
        html_fonte = page.content()
        city_match  = re.search(r'"key"\s*:\s*"city"\s*,\s*"value"\s*:\s*"([^"]+)"', html_fonte)
        state_match = re.search(r'"key"\s*:\s*"state"\s*,\s*"value"\s*:\s*"([^"]+)"', html_fonte)
        if city_match:
            dados["cidade"] = city_match.group(1)
        if state_match:
            dados["estado"] = state_match.group(1)

        nota_el = page.query_selector(
            "[class*='score'], [class*='Score'], "
            "[class*='rating'], [class*='Rating'], "
            "[data-testid*='score'], [aria-label*='nota']"
        )
        if nota_el:
            dados["nota_cliente"] = nota_el.inner_text().strip()

    except Exception as e:
        print(f"  [aviso] Erro ao extrair dados de {link}: {e}")

    return dados


def salvar_csv(reclamacoes, caminho, modo="w"):
    """Salva a lista de reclamações em CSV com encoding utf-8-sig."""
    campos = ["titulo", "data", "status", "cidade", "estado",
              "texto_preview", "link", "nota_cliente"]
    with open(caminho, mode=modo, encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        if modo == "w":
            writer.writeheader()
        writer.writerows(reclamacoes)


def coletar_passagem(page, status_param, label):
    """
    Percorre as páginas de listagem, coleta os links e acessa cada página individual.
    """
    todas = []

    for pagina in range(1, MAX_PAGINAS + 1):
        url = construir_url(status_param, pagina)
        print(f"Coletando página {pagina}/{MAX_PAGINAS} — {label} ...")

        ok = navegar_com_retry(page, url)
        if not ok:
            print(f"  [erro] Não foi possível carregar a página {pagina}. Encerrando passagem.")
            break

        esperar()
        aguardar_se_bot(page)

        links = extrair_links_pagina(page)

        if not links:
            print(f"  Nenhum card encontrado na página {pagina}. Encerrando passagem.")
            break

        print(f"  → {len(links)} links encontrados. Acessando páginas individuais...")

        for j, item in enumerate(links, 1):
            print(f"    [{j}/{len(links)}] {item['link'][-55:]}")
            dados = extrair_pagina_individual(page, item["link"], item["status"])
            if dados.get("titulo"):
                todas.append(dados)

        print(f"  Total acumulado: {len(todas)}")

    return todas


def main():
    os.makedirs(PASTA_DADOS, exist_ok=True)

    todas_reclamacoes = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, channel="chrome")
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
            locale="pt-BR",
        )
        page = context.new_page()
        Stealth().apply_stealth_sync(page)

        for passagem in STATUS_PASSAGENS:
            print(f"\n{'='*60}")
            print(f"Iniciando passagem: {passagem['label']}")
            print(f"{'='*60}")

            reclamacoes = coletar_passagem(page, passagem["status"], passagem["label"])
            todas_reclamacoes.extend(reclamacoes)

            # Salva após cada passagem para não perder progresso
            salvar_csv(todas_reclamacoes, ARQUIVO_SAIDA, modo="w")
            print(f"\nPassagem '{passagem['label']}' concluída: {len(reclamacoes)} reclamações.")
            print(f"Arquivo salvo com {len(todas_reclamacoes)} registros até agora.")

        browser.close()

    print(f"\n{'='*60}")
    print(f"Coleta finalizada. Total: {len(todas_reclamacoes)} reclamações.")
    print(f"Arquivo salvo em: {ARQUIVO_SAIDA}")


if __name__ == "__main__":
    main()
