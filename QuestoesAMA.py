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
        st.rerun()
    st.stop()

if "atividades_exibidas" not in st.session_state:
    st.session_state.atividades_exibidas = []

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
            )[["ATIVIDADE"]].head(10)

            if resultados.empty:
                st.info(f"Nenhuma atividade {nivel_titulo.lower()} encontrada.")
                continue

            if st.button(f"Selecionar tudo ({nivel_titulo})", key=f"select_all_{nivel_nome}"):
                for idx in resultados.index:
                    if len(st.session_state.atividades_exibidas) >= 10:
                        break
                    checkbox_key = f"chk_{idx}"
                    st.session_state[checkbox_key] = True
                    if idx not in st.session_state.atividades_exibidas:
                        st.session_state.atividades_exibidas.append(idx)
                st.rerun()

            for idx, row in resultados.iterrows():
                checkbox_key = f"chk_{idx}"
                if checkbox_key not in st.session_state:
                    st.session_state[checkbox_key] = False
                disabled = (
                    not st.session_state[checkbox_key] and len(st.session_state.atividades_exibidas) >= 10
                )
                checked = st.checkbox(row['ATIVIDADE'], key=checkbox_key, disabled=disabled)
                if checked and idx not in st.session_state.atividades_exibidas:
                    st.session_state.atividades_exibidas.append(idx)
                elif not checked and idx in st.session_state.atividades_exibidas:
                    st.session_state.atividades_exibidas.remove(idx)

    total = len(st.session_state.atividades_exibidas)
    st.progress(total / 10 if total <= 10 else 1.0)
    st.info(f"{total}/10 atividades escolhidas. Role a página para baixo.")

    if total >= 10:
     st.warning("10 Questões atingidas! Clique em PREENCHER CABEÇALHO ou Recomeçar tudo.")

    # Rolar até o botão
    st.markdown("""
    <script>
        setTimeout(function() {
            const el = document.getElementById("ancora_botao");
            if (el) {
                el.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }, 300);
    </script>
    """, unsafe_allow_html=True)


    if st.session_state.atividades_exibidas:
        st.markdown("<hr />", unsafe_allow_html=True)
        st.success("Links das atividades selecionadas:")
        col1, col2 = st.columns(2)
        for count, idx in enumerate(st.session_state.atividades_exibidas):
            nome = dados.loc[idx, "ATIVIDADE"]
            url_img = f"https://questoesama.pages.dev/{nome}.jpg"
            with col1 if count % 2 == 0 else col2:
                st.markdown(f"[Visualize esta atividade.]({url_img})", unsafe_allow_html=True)

        st.markdown("<div id='ancora_botao'></div>", unsafe_allow_html=True)


        if st.button("PREENCHER CABEÇALHO"):
            st.switch_page("pages/AtividadeAMA.py")

if st.button("Recomeçar tudo"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()