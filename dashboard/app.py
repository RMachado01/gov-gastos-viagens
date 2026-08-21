"""
Dashboard de Análise de Gastos com Viagens do Governo
Dados reais do Portal da Transparência (CGU)
Feito com Streamlit + Bootstrap 5 + Plotly
"""

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine

st.set_page_config(
    page_title="Gastos com Viagens do Governo",
    page_icon="✈️",
    layout="wide",
)

# Bootstrap 5 + CSS dos cards KPI
st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
    .card { border-radius: 10px; border: 1px solid #dee2e6; margin-bottom: 10px; }
    .card-body { padding: 1.2rem; }
    .kpi-valor { font-size: 1.7rem; font-weight: bold; color: #0d6efd; }
    .kpi-label { font-size: 0.85rem; color: #6c757d; margin-bottom: 6px; }
    .kpi-delta { font-size: 0.85rem; margin-top: 6px; }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def carregar_dados():
    engine = create_engine("sqlite:///data/processed/viagens.db")
    df = pd.read_sql("SELECT * FROM viagens", con=engine)
    df["ano"] = pd.to_numeric(df["ano"], errors="coerce").astype("Int64")
    return df


df = carregar_dados()

# ---- Header ----
st.markdown("""
<div class="container-fluid mb-3">
    <h1 class="display-5 fw-bold">✈️ Gastos com Viagens do Governo</h1>
    <p class="lead text-muted">Despesas com viagens de servidores públicos federais</p>
    <div class="alert alert-info py-2" role="alert">
        📌 <strong>Fonte:</strong> Portal da Transparência / CGU &nbsp;|&nbsp;
        <strong>Período:</strong> {min_ano} a {max_ano} &nbsp;|&nbsp;
        <strong>Registros:</strong> {total:,} viagens
    </div>
</div>
""".format(
    min_ano=int(df["ano"].min()),
    max_ano=int(df["ano"].max()),
    total=len(df),
), unsafe_allow_html=True)

# ---- Sidebar filtros ----
st.sidebar.header("🔍 Filtros")

anos_disponiveis = sorted(df["ano"].dropna().unique().astype(int))
ano_min, ano_max = st.sidebar.select_slider(
    "Período",
    options=anos_disponiveis,
    value=(min(anos_disponiveis), max(anos_disponiveis)),
)

# Top 30 órgãos por gasto total (evita lista gigante no filtro)
top_orgaos = (
    df.groupby("orgao")["valor_total"]
    .sum()
    .sort_values(ascending=False)
    .head(30)
    .index.tolist()
)
orgaos_selecionados = st.sidebar.multiselect(
    "Órgão (top 30 por gasto)",
    options=top_orgaos,
    default=top_orgaos,
)

# ---- Aplica filtros ----
df_f = df[
    df["ano"].between(ano_min, ano_max) &
    df["orgao"].isin(orgaos_selecionados)
]

if df_f.empty:
    st.warning("Nenhum dado para os filtros selecionados.")
    st.stop()

# ---- Helpers KPI ----
def badge_delta(delta):
    """Alta de gastos = ruim (vermelho), queda = bom (verde)."""
    if delta is None:
        return '<span class="badge bg-secondary">N/D</span>'
    if delta > 0:
        return f'<span class="badge bg-danger">↑ +{delta:.1f}%</span>'
    return f'<span class="badge bg-success">↓ {delta:.1f}%</span>'


def formata_real(valor):
    return f"R$ {valor:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")


anos_no_filtro = sorted(df_f["ano"].dropna().unique().astype(int))
ano_atual = anos_no_filtro[-1]
ano_ant = anos_no_filtro[-2] if len(anos_no_filtro) >= 2 else None


def delta_pct(atual, anterior):
    if not anterior or anterior == 0:
        return None
    return (atual - anterior) / anterior * 100


# Calcula valores por ano
gasto_atual = df_f[df_f["ano"] == ano_atual]["valor_total"].sum()
gasto_ant = df_f[df_f["ano"] == ano_ant]["valor_total"].sum() if ano_ant else 0

viagens_atual = len(df_f[df_f["ano"] == ano_atual])
viagens_ant = len(df_f[df_f["ano"] == ano_ant]) if ano_ant else 0

media_atual = df_f[df_f["ano"] == ano_atual]["valor_total"].mean()
media_ant = df_f[df_f["ano"] == ano_ant]["valor_total"].mean() if ano_ant else 0

orgao_top = df_f.groupby("orgao")["valor_total"].sum().idxmax()

# ---- KPIs ----
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="card">
        <div class="card-body">
            <div class="kpi-label">💰 Total Gasto ({ano_atual})</div>
            <div class="kpi-valor">{formata_real(gasto_atual)}</div>
            <div class="kpi-delta">vs {ano_ant}: {badge_delta(delta_pct(gasto_atual, gasto_ant))}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card">
        <div class="card-body">
            <div class="kpi-label">🧳 Viagens ({ano_atual})</div>
            <div class="kpi-valor">{viagens_atual:,}</div>
            <div class="kpi-delta">vs {ano_ant}: {badge_delta(delta_pct(viagens_atual, viagens_ant))}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="card">
        <div class="card-body">
            <div class="kpi-label">📊 Média por Viagem ({ano_atual})</div>
            <div class="kpi-valor">{formata_real(media_atual)}</div>
            <div class="kpi-delta">vs {ano_ant}: {badge_delta(delta_pct(media_atual, media_ant))}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    nome_curto = orgao_top[:35] + "..." if len(orgao_top) > 35 else orgao_top
    gasto_top = df_f.groupby("orgao")["valor_total"].sum().max()
    st.markdown(f"""
    <div class="card">
        <div class="card-body">
            <div class="kpi-label">🏆 Órgão que Mais Gastou</div>
            <div class="kpi-valor" style="font-size:1rem; line-height:1.4">{nome_curto}</div>
            <div class="kpi-delta">{formata_real(gasto_top)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---- Gráficos ----
col_a, col_b = st.columns(2)

with col_a:
    gastos_ano = df_f.groupby("ano")["valor_total"].sum().reset_index()
    fig = px.bar(
        gastos_ano, x="ano", y="valor_total",
        title="💸 Gastos Totais por Ano",
        labels={"ano": "Ano", "valor_total": "Total (R$)"},
        color_discrete_sequence=["#0d6efd"],
        text_auto=".2s",
    )
    fig.update_layout(margin=dict(t=40, b=0))
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    top10 = (
        df_f.groupby("orgao")["valor_total"]
        .sum().sort_values(ascending=True).tail(10).reset_index()
    )
    fig = px.bar(
        top10, x="valor_total", y="orgao", orientation="h",
        title="🏛️ Top 10 Órgãos por Gasto Total",
        labels={"orgao": "", "valor_total": "Total (R$)"},
        color_discrete_sequence=["#198754"],
    )
    fig.update_layout(margin=dict(t=40, b=0))
    st.plotly_chart(fig, use_container_width=True)

col_c, col_d = st.columns(2)

with col_c:
    evolucao = df_f.groupby("ano")["valor_total"].sum().reset_index()
    fig = px.line(
        evolucao, x="ano", y="valor_total",
        title="📈 Evolução do Gasto por Ano",
        labels={"ano": "Ano", "valor_total": "Total (R$)"},
        color_discrete_sequence=["#dc3545"],
        markers=True,
    )
    fig.update_layout(margin=dict(t=40, b=0))
    st.plotly_chart(fig, use_container_width=True)

with col_d:
    # Diárias vs Passagens vs Outros
    if "valor_diarias" in df_f.columns and "valor_passagens" in df_f.columns:
        outros = (df_f["valor_total"] - df_f["valor_diarias"] - df_f["valor_passagens"]).clip(lower=0).sum()
        breakdown = pd.DataFrame({
            "Tipo": ["Diárias", "Passagens", "Outros"],
            "Valor": [df_f["valor_diarias"].sum(), df_f["valor_passagens"].sum(), outros],
        })
        breakdown = breakdown[breakdown["Valor"] > 0]
        fig = px.pie(breakdown, values="Valor", names="Tipo", title="🧾 Composição dos Gastos")
    else:
        top5 = df_f.groupby("orgao")["valor_total"].sum().nlargest(5).reset_index()
        fig = px.pie(top5, values="valor_total", names="orgao", title="🧾 Top 5 Órgãos")
    fig.update_layout(margin=dict(t=40, b=0))
    st.plotly_chart(fig, use_container_width=True)

# ---- Footer ----
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
<div class="text-center text-muted" style="font-size:0.85rem; padding:10px">
    Dados reais do <strong>Portal da Transparência</strong> — Controladoria-Geral da União (CGU).
</div>
""", unsafe_allow_html=True)
