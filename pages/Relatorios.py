# pages/Relatorios.py
import streamlit as st
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

st.set_page_config(page_title="Relatórios AMA 2025", page_icon="📊")

ID_PLANILHA = "17SUODxQqwWOoC9Bns--MmEDEruawdeEZzNXuwh3ZIj8"

# --- AUTENTICAÇÃO ---
if "relatorio_autenticado" not in st.session_state:
    st.session_state.relatorio_autenticado = False

if not st.session_state.relatorio_autenticado:
    st.markdown("### 🔐 Acesso restrito aos professores")
    senha = st.text_input("Digite a senha para acessar os relatórios:", type="password")
    if senha == "sedu":
        st.session_state.relatorio_autenticado = True
        st.success("✅ Acesso autorizado!")
        st.rerun()
    elif senha:
        st.error("❌ Senha incorreta.")
    st.stop()

# --- FUNÇÃO DE CARREGAMENTO ---
@st.cache_data
def carregar_planilha(sheet_range):
    try:
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"])
        service = build("sheets", "v4", credentials=creds)
        result = service.spreadsheets().values().get(
            spreadsheetId=ID_PLANILHA,
            range=sheet_range
        ).execute()
        values = result.get("values", [])
        if not values or len(values) < 2:
            return pd.DataFrame()
        header = values[0]
        rows = [row + [None] * (len(header) - len(row)) for row in values[1:]]
        df = pd.DataFrame(rows, columns=header)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

# --- INTERFACE ---
st.title("📊 Relatórios de Atividades - AMA 2025")
st.markdown("Use o campo abaixo para buscar os dados de um código de atividade:")

codigo_input = st.text_input("🔍 Inserir Código Desejado:").strip().upper()

if codigo_input:
    st.markdown("---")
    st.markdown(f"### 🧾 Detalhes do código: `{codigo_input}`")

    df_geradas = carregar_planilha("ATIVIDADES_GERADAS!A1:Z")
    df_respostas = carregar_planilha("ATIVIDADES!B1:Z1000")
    gabarito_df = carregar_planilha("MATEMATICA!A1:N")

    atividades_do_codigo = df_geradas[df_geradas["CODIGO"] == codigo_input]
    respostas_do_codigo = df_respostas[df_respostas["CÓDIGO"] == codigo_input] if "CÓDIGO" in df_respostas.columns else pd.DataFrame()

    if atividades_do_codigo.empty:
        st.warning("❗ Código não encontrado na base de atividades geradas.")
    else:
        st.subheader("✅ Atividades Escolhidas pelo Professor:")
        atividades_listadas = [ativ for ativ in atividades_do_codigo.values[0][2:] if ativ]
        for i, ativ in enumerate(atividades_listadas, 1):
            gabarito = gabarito_df[gabarito_df["ATIVIDADE"] == ativ]["GABARITO"].values
            gabarito_texto = gabarito[0] if len(gabarito) > 0 else "?"
            st.markdown(f"{i}. **{ativ}** — Gabarito: `{gabarito_texto}`")

        if respostas_do_codigo.empty:
            st.info("ℹ️ Nenhuma resposta foi enviada ainda para este código.")
        else:
            st.markdown("### 👩‍🎓 Alunos que realizaram a atividade:")
            st.dataframe(respostas_do_codigo.iloc[:, :5], use_container_width=True)
