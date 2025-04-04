# pages/Relatorios.py
import streamlit as st
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

st.set_page_config(page_title="Relatórios AMA 2025", page_icon="📊")

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

# --- FUNÇÕES DE CARREGAMENTO ---
@st.cache_data
def carregar_planilha(sheet_range):
    try:
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
        )
        service = build("sheets", "v4", credentials=creds)
        sheet_id = "17SUODxQqwWOoC9Bns--MmEDEruawdeEZzNXuwh3ZIj8"

        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=sheet_range
        ).execute()

        values = result.get("values", [])
        if not values or len(values) < 2:
            return pd.DataFrame()

        headers = [h.strip().upper() for h in values[0]]
        data = [row + [None] * (len(headers) - len(row)) for row in values[1:]]
        return pd.DataFrame(data, columns=headers)

    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

# --- INTERFACE ---
st.title("📊 Relatórios de Atividades - AMA 2025")
st.markdown("Use o campo abaixo para buscar os dados de um código de atividade:")

codigo = st.text_input("🔍 Inserir Código Desejado:").strip().upper()

if codigo:
    st.markdown("---")
    st.markdown(f"### 🧾 Detalhes do código: `{codigo}`")

    df_geradas = carregar_planilha("ATIVIDADES_GERADAS!A1:Z")
    df_respostas = carregar_planilha("ATIVIDADES!A1:Z")

    atividades_do_codigo = df_geradas[df_geradas["CODIGO"] == codigo]
    respostas_do_codigo = df_respostas[df_respostas["CÓDIGO"] == codigo] if "CÓDIGO" in df_respostas.columns else pd.DataFrame()

    if atividades_do_codigo.empty:
        st.warning("❗ Código não encontrado na base de atividades geradas.")
    else:
        st.subheader("✅ Atividades Escolhidas pelo Professor:")
        atividades_listadas = [ativ for ativ in atividades_do_codigo.values[0][2:] if ativ]
        for i, ativ in enumerate(atividades_listadas, 1):
            st.markdown(f"{i}. **{ativ}**")

        if respostas_do_codigo.empty:
            st.info("Nenhuma resposta foi enviada ainda para este código.")
        else:
            st.markdown("### 👩‍🎓 Alunos que realizaram a atividade:")
            st.dataframe(respostas_do_codigo.iloc[:, :5], use_container_width=True)  # Timestamp, Código, Nome, Escola, Turma
