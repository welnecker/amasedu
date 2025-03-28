import streamlit as st
import pandas as pd
import requests
from io import StringIO

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
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<div style='height:140px'></div>", unsafe_allow_html=True)
st.markdown("""
<style>
    div.block-container {
        padding: 0.5rem 1rem 0.5rem 1rem;
    }
    .element-container {  
        margin-bottom: 0.25rem !important;
    }
    hr {
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("ATIVIDADE AMA 2025")

url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQhv1IMZCz0xYYNGiEIlrqzvsELrjozHr32CNYHdcHzVqYWwDUFolet_2XOxv4EX7Tu3vxOB4w-YUX9/pub?gid=2127889637&single=true&output=csv"

def carregar_dados():
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return pd.read_csv(StringIO(response.text))
    except Exception:
        return None

dados = carregar_dados()

if dados is None:
    st.error("❌ Erro ao carregar os dados da planilha do Google Sheets.")
    if st.button("🔄 Tentar novamente"):
        st.experimental_rerun()
    st.stop()

dados.columns = dados.columns.str.strip()
for col in ["SERIE", "HABILIDADE", "DESCRITOR", "NIVEL", "ATIVIDADE"]:
    if col in dados.columns:
        dados[col] = dados[col].astype(str).str.strip()

if "atividades_exibidas" not in st.session_state:
    st.session_state.atividades_exibidas = []

serie_opcoes = sorted(dados["SERIE"].dropna().unique())
st.markdown("### Escolha Série, Habilidade e Descritor.")
col_serie, col_habilidade, col_descritor = st.columns(3)

with col_serie:
    serie = st.selectbox("**SÉRIE**", ["Escolha..."] + serie_opcoes, key="serie")

with col_habilidade:
    habilidade_opcoes = sorted(dados[dados["SERIE"] == serie]["HABILIDADE"].dropna().unique()) if serie != "Escolha..." else []
    habilidade = st.selectbox("**HABILIDADE**", ["Escolha..."] + habilidade_opcoes, key="habilidade")

with col_descritor:
    descritor_opcoes = sorted(dados[(dados["SERIE"] == serie) & (dados["HABILIDADE"] == habilidade)]["DESCRITOR"].dropna().unique()) if habilidade != "Escolha..." else []
    descritor = st.selectbox("**DESCRITOR**", ["Escolha..."] + descritor_opcoes, key="descritor")

if descritor != "Escolha...":
    st.markdown("<hr />", unsafe_allow_html=True)
    st.subheader("ESCOLHA ATÉ 10 QUESTÕES.")

    total_selecionado = sum(
        1 for key in st.session_state if key.startswith("chk_") and st.session_state[key] is True
    )

    col_facil, col_medio, col_dificil = st.columns(3)
    niveis_fixos = {
        'Facil': ('Fácil', col_facil),
        'Medio': ('Médio', col_medio),
        'Dificil': ('Difícil', col_dificil),
    }

    for nivel_nome, (nivel_titulo, coluna) in niveis_fixos.items():
        with coluna:
            st.markdown(f"#### {nivel_titulo}")
            resultado_nivel = dados.query(
                'SERIE == @serie & HABILIDADE == @habilidade & DESCRITOR == @descritor & NIVEL == @nivel_nome'
            )[["ATIVIDADE"]].head(10)

            if not resultado_nivel.empty:
                if st.button(f"Selecionar tudo ({nivel_titulo})", key=f"btn_select_{nivel_nome}"):
                    for idx in resultado_nivel.index:
                        if len(st.session_state.atividades_exibidas) >= 10:
                            break
                        checkbox_key = f"chk_{idx}"
                        st.session_state[checkbox_key] = True
                        if idx not in st.session_state.atividades_exibidas:
                            st.session_state.atividades_exibidas.append(idx)
                    st.experimental_rerun()

            if resultado_nivel.empty:
                st.info(f"Nenhuma atividade {nivel_titulo.lower()} encontrada.")
            else:
                for idx, row in resultado_nivel.iterrows():
                    checkbox_key = f"chk_{idx}"
                    if checkbox_key not in st.session_state:
                        st.session_state[checkbox_key] = False

                    disabled = total_selecionado >= 10 and not st.session_state[checkbox_key]
                    checked = st.checkbox(row['ATIVIDADE'], key=checkbox_key, disabled=disabled)

                    if checked and idx not in st.session_state.atividades_exibidas:
                        st.session_state.atividades_exibidas.append(idx)
                    elif not checked and idx in st.session_state.atividades_exibidas:
                        st.session_state.atividades_exibidas.remove(idx)

    contador = len(st.session_state.atividades_exibidas)

    st.progress(contador / 10)
    st.info(f"{contador}/10 atividades escolhidas.")

    if contador >= 10:
        st.warning("10 Questões atingidas! Clique em PREENCHER CABEÇALHO ou Recomeçar tudo.")

    if st.session_state.atividades_exibidas:
        st.markdown("<hr />", unsafe_allow_html=True)
        st.success("Links das atividades selecionadas:")
        col1, col2 = st.columns(2)
        for count, idx in enumerate(st.session_state.atividades_exibidas):
            nome = dados.loc[idx, "ATIVIDADE"]
            url_img = f"https://questoesama.pages.dev/{nome}.jpg"
            coluna = col1 if count % 2 == 0 else col2
            coluna.markdown(f"- **{nome}**: <a href='{url_img}' target='_blank'>🔗 Visualize a atividade</a>", unsafe_allow_html=True)

        st.markdown("<hr />", unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            if st.button("📝 PREENCHER CABEÇALHO", key="btn_preencher"):
                st.switch_page("AtividadeAMA")  # Caminho mais seguro no Streamlit Cloud

        with col_btn2:
            if st.button("🔄 Recomeçar tudo", key="btn_recomecar"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.experimental_rerun()
