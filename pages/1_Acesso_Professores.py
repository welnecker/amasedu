import streamlit as st
import pandas as pd
import requests
from io import StringIO
import unicodedata
from datetime import datetime
import random
import string
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

st.set_page_config(page_title="ATIVIDADE AMA 2025", page_icon="📚")

if st.session_state.get("reiniciar_pedido"):
    st.session_state.clear()
    st.rerun()

# --- BLOQUEIO POR SENHA ---
if "relatorio_autenticado" not in st.session_state:
    st.session_state.relatorio_autenticado = False

if not st.session_state.relatorio_autenticado:
    st.markdown("### 🔐 Acesso restrito aos professores")
    email = st.text_input("Digite seu e-mail institucional:")
    if email.endswith("@educador.edu.es.gov.br"):
        st.session_state.relatorio_autenticado = True
        st.success("✅ Acesso autorizado!")
        st.rerun()
    elif email:
        st.error("❌ E-mail inválido. Use seu e-mail institucional.")
    st.stop()

st.markdown("### ✅ Versão atual: 01/04/2025 - 13h12")

# --- ESTILO VISUAL ---
st.markdown("""
<style>
.stApp {
    background-image: url("https://questoesama.pages.dev/img/fundo.png");
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center top;
    background-attachment: fixed;
}
.main > div {
    background-color: rgba(255, 255, 255, 0.85);
    padding: 2rem;
    border-radius: 15px;
    margin-top: 100px;
    box-shadow: 0 0 10px rgba(0,0,0,0.05);
}
div.block-container {
    padding: 0.5rem 1rem;
}
.element-container {
    margin-bottom: 0.25rem !important;
}
hr {
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div style='height:140px'></div>", unsafe_allow_html=True)
st.title("ATIVIDADE AMA 2025")

# --- ESCOLHA DA DISCIPLINA ---
st.markdown("### Escolha a disciplina:")
col1, col2 = st.columns(2)

if "disciplina" not in st.session_state:
    st.session_state.disciplina = None

botao_matematica = col1.button("📘 MATEMÁTICA", disabled=st.session_state.disciplina is not None)
botao_portugues = col2.button("📗 LÍNGUA PORTUGUESA", disabled=st.session_state.disciplina is not None)

if botao_matematica:
    st.session_state.disciplina = "MATEMATICA"
    st.rerun()

if botao_portugues:
    st.session_state.disciplina = "PORTUGUES"
    st.rerun()

if not st.session_state.disciplina:
    st.warning("Selecione uma disciplina para continuar.")
    st.stop()

# Mensagem de confirmação com destaque visual
st.markdown(
    f"<div style='padding:10px; background-color:#dff0d8; border-radius:10px;'><b>✅ Disciplina selecionada:</b> {st.session_state.disciplina}</div>",
    unsafe_allow_html=True
)

# --- CARREGAMENTO DE BASE_SEGES ---
URL_BASE_SEGES = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQhv1IMZCz0xYYNGiEIlrqzvsELrjozHr32CNYHdcHzVqYWwDUFolet_2XOxv4EX7Tu3vxOB4w-YUX9/pub?gid=340515451&single=true&output=csv"

@st.cache_data(show_spinner=False)
def carregar_base_seges():
    def normalizar_coluna(col):
        return ''.join(c for c in unicodedata.normalize('NFD', col) if unicodedata.category(c) != 'Mn').strip().upper()
    try:
        response = requests.get(URL_BASE_SEGES, timeout=10)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text))
        df.columns = [normalizar_coluna(c) for c in df.columns]
        return df
    except Exception:
        return pd.DataFrame()

base_seges = carregar_base_seges()
colunas_necessarias = {"SRE", "ESCOLA", "TURMA"}

if not base_seges.empty and colunas_necessarias.issubset(base_seges.columns):
    st.markdown("### Escolha a SRE, Escola e Turma:")
    col_sre, col_escola, col_turma = st.columns(3)

    sre = col_sre.selectbox("**SRE**", ["Escolha..."] + sorted(base_seges["SRE"].dropna().unique()), key="sre")
    escolas = base_seges[base_seges["SRE"] == sre]["ESCOLA"].dropna().unique() if sre != "Escolha..." else []
    escola = col_escola.selectbox("**ESCOLA**", ["Escolha..."] + sorted(escolas), key="escola")
    turmas = base_seges[(base_seges["SRE"] == sre) & (base_seges["ESCOLA"] == escola)]["TURMA"].dropna().unique() if escola != "Escolha..." else []
    turma = col_turma.selectbox("**TURMA**", ["Escolha..."] + sorted(turmas), key="turma")

    st.session_state.selecionado_sre = sre
    st.session_state.selecionado_escola = escola
    st.session_state.selecionado_turma = turma
else:
    st.warning("⚠️ A aba BASE_SEGES está vazia ou com colunas inválidas. Verifique se contém 'SRE', 'ESCOLA' e 'TURMA'.")

# --- CARREGAMENTO DE DADOS DAS QUESTÕES ---
GIDS = {
    "MATEMATICA": "2127889637",
    "PORTUGUES": "1217179376"
}
URL_PLANILHA_QUESTOES = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vQhv1IMZCz0xYYNGiEIlrqzvsELrjozHr32CNYHdcHzVqYWwDUFolet_2XOxv4EX7Tu3vxOB4w-YUX9/pub?gid={GIDS[st.session_state.disciplina]}&single=true&output=csv"

@st.cache_data(show_spinner=False)
def carregar_dados():
    try:
        response = requests.get(URL_PLANILHA_QUESTOES, timeout=10)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text))
        df.columns = df.columns.str.strip()
        for col in ["SERIE", "HABILIDADE", "DESCRITOR", "NIVEL", "ATIVIDADE"]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        return df
    except Exception:
        return None

dados = carregar_dados()
if dados is None:
    st.error("❌ Erro ao carregar os dados da planilha de questões.")
    if st.button("🔄 Tentar novamente"):
        st.rerun()
    st.stop()

# --- FILTROS ---
st.markdown("### Escolha Série, Habilidade e Descritor.")
col_serie, col_habilidade, col_descritor = st.columns(3)

serie = col_serie.selectbox("**SÉRIE**", ["Escolha..."] + sorted(dados["SERIE"].dropna().unique()), key="serie")
habilidade = col_habilidade.selectbox("**HABILIDADE**",
    ["Escolha..."] + sorted(dados[dados["SERIE"] == serie]["HABILIDADE"].dropna().unique()) if serie != "Escolha..." else [],
    key="habilidade"
)
descritor = col_descritor.selectbox("**DESCRITOR**",
    ["Escolha..."] + sorted(dados[(dados["SERIE"] == serie) & (dados["HABILIDADE"] == habilidade)]["DESCRITOR"].dropna().unique()) if habilidade != "Escolha..." else [],
    key="descritor"
)

# --- GERAÇÃO DE ATIVIDADES ---
if descritor != "Escolha...":
    atividades = dados.query(
        'SERIE == @serie & HABILIDADE == @habilidade & DESCRITOR == @descritor'
    )["ATIVIDADE"].head(10)

    st.markdown("### Atividades selecionadas:")
    for atividade in atividades:
        st.write(f"- {atividade}")

    if st.button("Gerar Atividade"):
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        linha_unica = [timestamp, "CÓDIGO", sre, escola, turma, serie, habilidade, descritor] + list(atividades) + [st.session_state.disciplina]
        # Aqui você enviaria essa linha para a planilha ATIVIDADES_GERADAS
        st.write("Atividade gerada com sucesso.")
