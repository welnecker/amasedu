# app.py (página inicial com proteção por senha para professores)
import streamlit as st
import pandas as pd
import requests
from io import StringIO

st.set_page_config(page_title="ATIVIDADE AMA 2025", page_icon="📚")

# --- BLOQUEIO POR SENHA ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("### Área restrita para professores")
    senha = st.text_input("Digite a senha para continuar:", type="password")
    if senha == "sedu":
        st.session_state.autenticado = True
        st.success("Acesso autorizado!")
        st.rerun()
    elif senha:
        st.error("Senha incorreta. Tente novamente.")
    st.stop()

st.markdown("### ✅ Versão atual: 01/04/2025 - 13h12")

# --- ESTILO VISUAL ---
st.markdown(
    """
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
    """,
    unsafe_allow_html=True
)

st.markdown("<div style='height:140px'></div>", unsafe_allow_html=True)

# --- CARREGAMENTO DE DADOS ---
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQhv1IMZCz0xYYNGiEIlrqzvsELrjozHr32CNYHdcHzVqYWwDUFolet_2XOxv4EX7Tu3vxOB4w-YUX9/pub?gid=2127889637&single=true&output=csv"
URL_BASE_SEGES = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQhv1IMZCz0xYYNGiEIlrqzvsELrjozHr32CNYHdcHzVqYWwDUFolet_2XOxv4EX7Tu3vxOB4w-YUX9/pub?gid=1840243180&single=true&output=csv"

@st.cache_data(show_spinner=False)
def carregar_dados():
    try:
        response = requests.get(URL_PLANILHA, timeout=10)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text))
        df.columns = df.columns.str.strip()
        for col in ["SERIE", "HABILIDADE", "DESCRITOR", "NIVEL", "ATIVIDADE"]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        return df
    except Exception:
        return None

@st.cache_data(show_spinner=False)
def carregar_base_seges():
    try:
        response = requests.get(URL_BASE_SEGES, timeout=10)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text))
        df.columns = df.columns.str.strip().str.upper()
        return df
    except Exception:
        return pd.DataFrame()

dados = carregar_dados()
base_seges = carregar_base_seges()

if dados is None:
    st.error("❌ Erro ao carregar os dados da planilha do Google Sheets.")
    if st.button("🔄 Tentar novamente"):
        st.rerun()
    st.stop()

if "atividades_exibidas" not in st.session_state:
    st.session_state.atividades_exibidas = []

# --- FILTROS ADICIONAIS ---
if not base_seges.empty:
    col_sre, col_escola, col_turma = st.columns(3)

    sre = col_sre.selectbox("**SRE**", sorted(base_seges["SRE"].dropna().unique()), key="sre")
    escolas = base_seges[base_seges["SRE"] == sre]["ESCOLA"].dropna().unique()
    escola = col_escola.selectbox("**ESCOLA**", sorted(escolas), key="escola")
    turmas = base_seges[(base_seges["SRE"] == sre) & (base_seges["ESCOLA"] == escola)]["TURMA"].dropna().unique()
    turma = col_turma.selectbox("**TURMA**", sorted(turmas), key="turma")

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

# --- TÍTULO PRINCIPAL ---
st.title("ATIVIDADE AMA 2025")

# --- EXIBIÇÃO DE QUESTÕES ---
if descritor != "Escolha...":
    ...
