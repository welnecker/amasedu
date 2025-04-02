# app.py (página inicial com proteção por senha para professores)
import streamlit as st
import pandas as pd
import requests
from io import StringIO

st.set_page_config(page_title="ATIVIDADE AMA 2025", page_icon="📚")

container = st.empty()
final_container = st.empty()

# --- BLOQUEIO POR SENHA ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("### Área restrita para professores")
    senha = st.text_input("Digite a senha para continuar:", type="password")
    if senha == "sedu":
        st.session_state.autenticado = True
        st.success("Acesso autorizado!")
        st.experimental_rerun()
    elif senha:
        st.error("Senha incorreta. Tente novamente.")
    st.stop()

# Versão
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

# --- CARREGAMENTO DE DADOS ---
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQhv1IMZCz0xYYNGiEIlrqzvsELrjozHr32CNYHdcHzVqYWwDUFolet_2XOxv4EX7Tu3vxOB4w-YUX9/pub?gid=2127889637&single=true&output=csv"

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

dados = carregar_dados()
if dados is None:
    st.error("❌ Erro ao carregar os dados da planilha do Google Sheets.")
    if st.button("🔄 Tentar novamente"):
        st.experimental_rerun()
    st.stop()

if "atividades_exibidas" not in st.session_state:
    st.session_state.atividades_exibidas = []
    st.session_state.total = 0

if st.button("Recomeçar tudo", key="recomecar"):
    st.session_state.atividades_exibidas = []
    st.session_state.total = 0
    st.experimental_rerun()

st.markdown("### Selecione os filtros:")

col1, col2, col3 = st.columns(3)

with col1:
    serie = st.selectbox("Série:", ["Escolha..."] + sorted(dados["SERIE"].unique()))

with col2:
    habilidade = st.selectbox("Habilidade:", ["Escolha..."] + sorted(dados["HABILIDADE"].unique()))

with col3:
    descritor = st.selectbox("Descritor:", ["Escolha..."] + sorted(dados["DESCRITOR"].unique()))

nivel = st.radio("Nível:", ["FÁCIL", "MÉDIO", "DIFÍCIL"], horizontal=True)

st.markdown("""
    <a href="#final" style="text-decoration:none;">
        <button style="background-color:#4CAF50;color:white;padding:10px;border:none;border-radius:5px;cursor:pointer;">
            Ir para o final
        </button>
    </a>
    """, unsafe_allow_html=True)

if st.session_state.atividades_exibidas:
    st.markdown("### Atividades selecionadas:")
    for idx, atividade in enumerate(st.session_state.atividades_exibidas, 1):
        st.markdown(f"**{idx}. {atividade}**")
    
    st.markdown(f"**Total de atividades: {st.session_state.total}**")

if descritor != "Escolha...":
    filtro = dados[(dados["SERIE"] == serie) & 
                   (dados["HABILIDADE"] == habilidade) & 
                   (dados["DESCRITOR"] == descritor) & 
                   (dados["NIVEL"] == nivel)]
    
    if not filtro.empty:
        atividade = filtro["ATIVIDADE"].iloc[0]
        if st.button("Adicionar Atividade"):
            if atividade not in st.session_state.atividades_exibidas:
                st.session_state.atividades_exibidas.append(atividade)
                st.session_state.total += 1
                st.experimental_rerun()
            else:
                st.warning("Esta atividade já foi adicionada.")
    else:
        st.warning("Nenhuma atividade encontrada com os filtros selecionados.")

total = st.session_state.total

if total >= 10:
    container.warning("10 Questões atingidas! Clique em PREENCHER CABEÇALHO ou Recomeçar tudo.")
    final_container.markdown("## Fim da seleção")

if st.button("PREENCHER CABEÇALHO"):
    st.session_state.preencher_cabecalho = True
    st.experimental_rerun()

if "preencher_cabecalho" in st.session_state and st.session_state.preencher_cabecalho:
    st.markdown("### Preencha o cabeçalho:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        nome_escola = st.text_input("Nome da escola:")
        nome_professor = st.text_input("Nome do professor:")
    
    with col2:
        nome_aluno = st.text_input("Nome do aluno:")
        turma = st.text_input("Turma:")
    
        if st.button("Gerar PDF"):
        if nome_escola and nome_professor and nome_aluno and turma:
            st.success("PDF gerado com sucesso!")
            # Aqui você pode adicionar a lógica para gerar o PDF
            # Por exemplo, usar uma biblioteca como reportlab ou fpdf
            # e criar um link para download do PDF gerado
        else:
            st.error("Por favor, preencha todos os campos do cabeçalho.")

st.markdown("<div id='final'></div>", unsafe_allow_html=True)

# Adicione informações de rodapé ou créditos aqui, se necessário
st.markdown("---")
st.markdown("Desenvolvido pela Equipe de Tecnologia Educacional - SEDU/ES")

