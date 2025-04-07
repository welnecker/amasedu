# app.py (página inicial com proteção por senha para professores)
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
st.title("ATIVIDADE AMA 2025")

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

# --- CARREGAMENTO DE DADOS PARA QUESTÕES ---
URL_PLANILHA_QUESTOES = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQhv1IMZCz0xYYNGiEIlrqzvsELrjozHr32CNYHdcHzVqYWwDUFolet_2XOxv4EX7Tu3vxOB4w-YUX9/pub?gid=2127889637&single=true&output=csv"

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

if "atividades_exibidas" not in st.session_state:
    st.session_state.atividades_exibidas = []

# --- FILTROS ANTIGOS ---
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

# --- EXIBIÇÃO DE QUESTÕES ---
if descritor != "Escolha...":
    st.markdown("<hr />", unsafe_allow_html=True)
    st.subheader("ESCOLHA ATÉ 10 QUESTÕES.")

    total_selecionado = len(st.session_state.atividades_exibidas)
    col_facil, col_medio, col_dificil = st.columns(3)
    niveis_fixos = {'Facil': ('Fácil', col_facil), 'Medio': ('Médio', col_medio), 'Dificil': ('Difícil', col_dificil)}

    for nivel_nome, (nivel_titulo, coluna) in niveis_fixos.items():
        with coluna:
            st.markdown(f"#### {nivel_titulo}")
            resultados = dados.query(
                'SERIE == @serie & HABILIDADE == @habilidade & DESCRITOR == @descritor & NIVEL == @nivel_nome'
            )["ATIVIDADE"].head(10)

            if resultados.empty:
                st.info(f"Nenhuma atividade {nivel_titulo.lower()} encontrada.")
                continue

            if st.button(f"Selecionar tudo ({nivel_titulo})", key=f"select_all_{nivel_nome}"):
                for nome_atividade in resultados:
                    if nome_atividade not in st.session_state.atividades_exibidas and len(st.session_state.atividades_exibidas) < 10:
                        st.session_state.atividades_exibidas.append(nome_atividade)
                st.rerun()

            for idx, nome_atividade in enumerate(resultados):
                checkbox_key = f"chk_{nivel_nome}_{idx}"
                checked = nome_atividade in st.session_state.atividades_exibidas
                disabled = not checked and len(st.session_state.atividades_exibidas) >= 10

                if st.checkbox(nome_atividade, key=checkbox_key, value=checked, disabled=disabled):
                    if nome_atividade not in st.session_state.atividades_exibidas and len(st.session_state.atividades_exibidas) < 10:
                        st.session_state.atividades_exibidas.append(nome_atividade)
                elif nome_atividade in st.session_state.atividades_exibidas:
                    st.session_state.atividades_exibidas.remove(nome_atividade)

    total = len(st.session_state.atividades_exibidas)
    st.progress(total / 10 if total <= 10 else 1.0)
    st.info(f"{total}/10 atividades escolhidas. Role a página para baixo.")

    if total >= 10:
        st.warning("10 Questões atingidas! Clique em PREENCHER CABEÇALHO ou Recomeçar tudo.")

    if st.session_state.atividades_exibidas:
        st.markdown("<hr />", unsafe_allow_html=True)
        st.success("Links das atividades selecionadas:")
        col1, col2 = st.columns(2)
        for count, nome in enumerate(st.session_state.atividades_exibidas):
            url_img = f"https://questoesama.pages.dev/{nome}.jpg"
            with col1 if count % 2 == 0 else col2:
                st.markdown(f"[Visualize esta atividade.]({url_img})", unsafe_allow_html=True)

        if st.button("PREENCHER CABEÇALHO"):
            st.switch_page("pages/AtividadeAMA.py")

if st.button("Recomeçar tudo"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
