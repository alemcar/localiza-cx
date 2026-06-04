"""
Dashboard interativo de CX da Localiza — Reclame Aqui.
Execute com: streamlit run 3_dashboard.py
"""

import os
import pandas as pd
import plotly.express as px
import streamlit as st

# Caminho do arquivo processado
PASTA_DADOS = os.path.join(os.path.dirname(__file__), "dados")
ARQUIVO = os.path.join(PASTA_DADOS, "reclamacoes_processadas.csv")


@st.cache_data
def carregar_dados():
    """Carrega o CSV processado. Exibe erro claro se o arquivo não existir."""
    if not os.path.exists(ARQUIVO):
        st.error(f"Arquivo não encontrado: {ARQUIVO}\nExecute `python 2_processar.py` primeiro.")
        st.stop()
    df = pd.read_csv(ARQUIVO, encoding="utf-8-sig")
    df["nota_cliente"] = pd.to_numeric(df["nota_cliente"], errors="coerce")
    return df


def aplicar_filtros(df, estados_sel, categorias_sel):
    """Aplica os filtros de estado e categoria ao DataFrame."""
    if "Todos" not in estados_sel:
        df = df[df["estado"].isin(estados_sel)]
    if "Todos" not in categorias_sel:
        df = df[df["categoria"].isin(categorias_sel)]
    return df


st.set_page_config(page_title="Análise de CX — Localiza", layout="wide")

# CSS: títulos grandes em verde, textos menores em branco
st.markdown("""
    <style>
        h1, h2, h3 {
            color: #7DDF20 !important;
        }
        div[data-testid="stTooltipContent"] {
            color: #7DDF20 !important;
        }
    </style>
""", unsafe_allow_html=True)

df = carregar_dados()

st.title("Análise de CX — Localiza no Reclame Aqui")
st.caption(f"Total de registros: {len(df):,}  |  Fonte: Reclame Aqui")

st.sidebar.header("Filtros")
opcoes_estados = ["Todos"] + sorted(df["estado"].dropna().unique().tolist())
estados_sel = st.sidebar.multiselect("Estado", options=opcoes_estados, default=["Todos"])
opcoes_categorias = ["Todos"] + sorted(df["categoria"].dropna().unique().tolist())
categorias_sel = st.sidebar.multiselect("Categoria", options=opcoes_categorias, default=["Todos"])

df_filtrado = aplicar_filtros(df.copy(), estados_sel, categorias_sel)
df_com_nota = df_filtrado[df_filtrado["nota_cliente"].notna()].copy()

col1, col2, col3 = st.columns(3)
total = len(df_filtrado)
nota_media_geral = df_filtrado["nota_cliente"].mean()
nota_str = f"{nota_media_geral:.1f}" if pd.notna(nota_media_geral) else "—"
media_geral = round(nota_media_geral, 1) if pd.notna(nota_media_geral) else None

# Taxa de resolução: % de reclamações efetivamente resolvidas (avaliadas positivamente pelo cliente)
resolvidas = df_filtrado["status"].str.upper().eq("RESOLVIDO").sum()
pct_resolucao = (resolvidas / total * 100) if total > 0 else 0

col1.metric("Total de reclamações", f"{total:,}")
col2.metric("Nota média do cliente", nota_str)
col3.metric("Taxa de resolução", f"{pct_resolucao:.1f}%",
            help="% de reclamações com status RESOLVIDO (avaliadas positivamente pelo cliente)")

st.divider()

st.subheader("Distribuição das reclamações")

c1, c2 = st.columns(2)

with c1:
    contagem_cat = (
        df_filtrado["categoria"]
        .value_counts()
        .reset_index()
        .rename(columns={"count": "quantidade"})
        .sort_values("quantidade", ascending=False)
    )
    fig = px.bar(
        contagem_cat,
        x="categoria",
        y="quantidade",
        title="Reclamações por categoria",
        color="categoria",
        text="quantidade",
        labels={"quantidade": "Qtd", "categoria": ""},
        color_discrete_sequence=['#d90000','#de2906','#e33e0e','#e84d15','#ec5d1c','#f16b23','#f67728','#ff8026'],
    )
    fig.update_traces(textposition="outside", texttemplate="<b>%{text}</b>", textfont={"color": "black"})
    fig.update_layout(
        showlegend=False,
        xaxis_tickangle=-30,
        yaxis_visible=False,
        uniformtext_minsize=10,
        uniformtext_mode="hide",
    )
    st.plotly_chart(fig, use_container_width=True)

with c2:
    top_estados = (
        df_filtrado["estado"]
        .value_counts()
        .head(10)
        .reset_index()
        .rename(columns={"count": "quantidade"})
        .sort_values("quantidade", ascending=True)
    )
    fig = px.bar(
        top_estados,
        x="quantidade",
        y="estado",
        orientation="h",
        title="Volume de reclamações por Estado",
        color="estado",
        text="quantidade",
        labels={"quantidade": "Qtd", "estado": ""},
        color_discrete_sequence=['#ff8026','#f7792a','#f37025','#ef6620','#ec5a1b','#e85016','#e44310','#e1340a','#dd2304','#d90000'],
    )
    fig.update_traces(textposition="outside", texttemplate="<b>%{text}</b>", textfont={"color": "black"})
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

top_cidades = (
    df_filtrado["cidade"]
    .value_counts()
    .head(10)
    .reset_index()
    .rename(columns={"count": "quantidade"})
    .sort_values("quantidade", ascending=True)
)
fig = px.bar(
    top_cidades,
    x="quantidade",
    y="cidade",
    orientation="h",
    title="Volume de reclamações por cidade",
    color="cidade",
    text="quantidade",
    labels={"quantidade": "Qtd", "cidade": ""},
    color_discrete_sequence=['#ff8026','#f7792a','#f37025','#ef6620','#ec5a1b','#e85016','#e44310','#e1340a','#dd2304','#d90000'],
)
fig.update_traces(textposition="outside", texttemplate="<b>%{text}</b>", textfont={"color": "black"})
fig.update_layout(showlegend=False)
st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("Correlações com nota do cliente")
st.caption(f"{len(df_com_nota):,} reclamações com nota disponível")

c3, c4 = st.columns(2)

with c3:
    if len(df_com_nota) > 0:
        nota_cat = (
            df_com_nota.groupby("categoria")["nota_cliente"]
            .mean()
            .round(1)
            .reset_index()
            .rename(columns={"nota_cliente": "nota_media"})
            .sort_values("nota_media", ascending=False)
        )
        # Barras verticais com linha de referência da média geral
        fig = px.bar(
            nota_cat,
            x="categoria",
            y="nota_media",
            title="Nota média por categoria",
            color="categoria",
            text="nota_media",
            labels={"nota_media": "Nota média", "categoria": ""},
            color_discrete_sequence=['#ff8026','#f67728','#f16b23','#ec5d1c','#e84d15','#e33e0e','#de2906','#d90000'],
        )
        fig.update_traces(textposition="outside", texttemplate="<b>%{text}</b>", textfont={"color": "black"})
        if media_geral:
            fig.add_hline(
                y=media_geral,
                line_dash="dash",
                line_color="gray",
                layer="below",
                annotation_text=f"Média geral: {media_geral}",
                annotation_position="right",
            )
        fig.update_layout(
            coloraxis_showscale=False,
            showlegend=False,
            xaxis_tickangle=-30,
            yaxis_visible=False,
            margin=dict(r=130),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem notas disponíveis.")

with c4:
    if len(df_com_nota) > 0:
        nota_estado = (
            df_com_nota.groupby("estado")["nota_cliente"]
            .mean()
            .round(1)
            .reset_index()
            .rename(columns={"nota_cliente": "nota_media"})
            .sort_values("nota_media", ascending=True)
            .head(10)
        )
        fig = px.bar(
            nota_estado,
            x="nota_media",
            y="estado",
            orientation="h",
            title="Estados com menor índice de satisfação",
            color="estado",
            text="nota_media",
            labels={"nota_media": "Nota média", "estado": ""},
            color_discrete_sequence=['#d90000','#dd2304','#e1340a','#e44310','#e85016','#ec5a1b','#ef6620','#f37025','#f7792a','#ff8026'],
        )
        fig.update_traces(textposition="outside", texttemplate="<b>%{text}</b>", textfont={"color": "black"})
        fig.update_layout(showlegend=False)
        if media_geral:
            fig.add_vline(
                x=media_geral,
                line_dash="dash",
                line_color="gray",
                layer="below",
                annotation_text=f"Média geral: {media_geral}",
                annotation_position="top",
            )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem notas disponíveis.")

st.divider()
st.subheader("Reclamações por categoria — Belo Horizonte")

df_bh = df_filtrado[df_filtrado["cidade"].str.strip().str.lower() == "belo horizonte"]

if len(df_bh) > 0:
    contagem_bh = (
        df_bh["categoria"]
        .value_counts()
        .reset_index()
        .rename(columns={"count": "quantidade"})
        .sort_values("quantidade", ascending=False)
    )
    fig = px.bar(
        contagem_bh,
        x="categoria",
        y="quantidade",
        title=f"Reclamações por categoria — Belo Horizonte ({len(df_bh)} reclamações)",
        color="categoria",
        text="quantidade",
        labels={"quantidade": "Qtd", "categoria": ""},
        color_discrete_sequence=['#d90000','#de2906','#e33e0e','#e84d15','#ec5d1c','#f16b23','#f67728','#ff8026'],
    )
    fig.update_traces(textposition="outside", texttemplate="<b>%{text}</b>", textfont={"color": "black"})
    fig.update_layout(showlegend=False, xaxis_tickangle=-30, yaxis_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    df_bh_nota = df_bh[df_bh["nota_cliente"].notna()]
    if len(df_bh_nota) > 0:
        nota_bh = (
            df_bh_nota.groupby("categoria")["nota_cliente"]
            .mean()
            .round(1)
            .reset_index()
            .rename(columns={"nota_cliente": "nota_media"})
            .sort_values("nota_media", ascending=False)
        )
        media_bh = round(df_bh_nota["nota_cliente"].mean(), 1)
        fig = px.bar(
            nota_bh,
            x="categoria",
            y="nota_media",
            title="Nota média por categoria — Belo Horizonte",
            color="categoria",
            text="nota_media",
            labels={"nota_media": "Nota média", "categoria": ""},
            color_discrete_sequence=['#d90000','#de2906','#e33e0e','#e84d15','#ec5d1c','#f16b23','#f67728','#ff8026'],
        )
        fig.update_traces(textposition="outside", texttemplate="<b>%{text}</b>", textfont={"color": "black"})
        fig.add_hline(
            y=media_bh,
            line_dash="dash",
            line_color="gray",
            layer="below",
            annotation_text=f"Média BH: {media_bh}",
            annotation_position="right",
        )
        fig.update_layout(showlegend=False, xaxis_tickangle=-30, yaxis_visible=False, margin=dict(r=120))
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Nenhuma reclamação encontrada para Belo Horizonte com os filtros selecionados.")

st.divider()

st.subheader("Reclamações")
colunas_tabela = [c for c in ["titulo", "status", "cidade", "estado", "categoria", "nota_cliente"]
                  if c in df_filtrado.columns]
df_tabela = df_filtrado[colunas_tabela].copy()

st.dataframe(
    df_tabela,
    column_config={
        "nota_cliente": st.column_config.ProgressColumn(
            "nota_cliente",
            min_value=0,
            max_value=10,
            format="%.0f",
        )
    },
    use_container_width=True,
)
