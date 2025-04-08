# Página: Relatorios (adicionando correção de busca por código + botão 'Atualizar Lista')
import streamlit as st
import pandas as pd
import requests
from io import StringIO

st.set_page_config(page_title="Relatórios", page_icon="📊")

st.title("📊 Relatórios de Atividades")

URL_ATIVIDADES = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQhv1IMZCz0xYYNGiEIlrqzvsELrjozHr32CNYHdcHzVqYWwDUFolet_2XOxv4EX7Tu3vxOB4w-YUX9/pub?gid=1838964815&single=true&output=csv"

@st.cache_data(show_spinner=False)
def carregar_atividades():
    try:
        response = requests.get(URL_ATIVIDADES, timeout=10)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text))
        df.columns = df.columns.str.strip().str.upper()
        return df
    except Exception:
        return pd.DataFrame()

if "codigo_filtro" not in st.session_state:
    st.session_state.codigo_filtro = ""

codigo = st.text_input("Inserir Código Desejado:", value=st.session_state.codigo_filtro)
col1, col2 = st.columns([3,1])
col1.text_input("Inserir Código Desejado:", value=codigo, key="codigo_input")
if col2.button("🔄 Atualizar Lista"):
    st.session_state.codigo_filtro = st.session_state.codigo_input
    st.rerun()

atividades_df = carregar_atividades()

if atividades_df.empty:
    st.warning("Não foi possível carregar a aba ATIVIDADES.")
    st.stop()

codigo_busca = st.session_state.codigo_filtro.strip()
if codigo_busca:
    atividades_df.columns = atividades_df.columns.str.upper()
    col_codigo = "CÓDIGO" if "CÓDIGO" in atividades_df.columns else "CODIGO"
    if col_codigo in atividades_df.columns:
        resultados = atividades_df[atividades_df[col_codigo].astype(str).str.strip() == codigo_busca]
        if resultados.empty:
            st.info("Nenhum resultado encontrado para o código informado.")
        else:
            st.success(f"{len(resultados)} registro(s) encontrado(s) com o código: {codigo_busca}")
            st.dataframe(resultados)
    else:
        st.error("Coluna de código não encontrada na planilha.")
else:
    st.info("Digite um código e clique em 'Atualizar Lista' para ver os resultados.")
