import streamlit as st
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

st.set_page_config(page_title="Relatórios AMA 2025", page_icon="📊")

# --- Autenticação por senha ---
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

# --- Função para carregar dados do Google Sheets ---
@st.cache_data(show_spinner=False)
def carregar_dados(sheet_range, has_header=True):
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"])
    service = build("sheets", "v4", credentials=creds)
    result = service.spreadsheets().values().get(
        spreadsheetId="17SUODxQqwWOoC9Bns--MmEDEruawdeEZzNXuwh3ZIj8",
        range=sheet_range
    ).execute()

    values = result.get("values", [])
    if not values or len(values) < 1:
        return pd.DataFrame()

    if has_header:
        header = [col.strip().upper() for col in values[0]]
        data = values[1:]
        return pd.DataFrame(data, columns=header)
    else:
        return pd.DataFrame(values)

# --- Interface ---
st.title("📊 Relatórios de Atividades - AMA 2025")
st.markdown("Use o campo abaixo para buscar os dados de um código de atividade:")

codigo = st.text_input("🔍 Inserir Código Desejado:").strip().upper()

if codigo:
    st.markdown("---")
    st.markdown(f"### 🧾 Detalhes do código: `{codigo}`")

    df_geradas = carregar_dados("ATIVIDADES_GERADAS!A1:Z", has_header=True)
    df_respostas = carregar_dados("ATIVIDADES!A1:Z", has_header=True)
    df_gabarito = carregar_dados("MATEMATICA!A1:N", has_header=True)

    # Lista de atividades do professor
    atividades_do_codigo = df_geradas[df_geradas["CODIGO"] == codigo]
    if atividades_do_codigo.empty:
        st.warning("❗ Código não encontrado na base de atividades geradas.")
        st.stop()

    atividades_escolhidas = [a for a in atividades_do_codigo.values[0][2:] if a]
    st.subheader("✅ Atividades Escolhidas pelo Professor:")

    for i, nome in enumerate(atividades_escolhidas, 1):
        gabarito = df_gabarito[df_gabarito["ATIVIDADE"] == nome]["GABARITO"]
        letra = gabarito.values[0] if not gabarito.empty else "?"
        st.markdown(f"{i}. **{nome}** - Gabarito: **{letra}**")

    # Filtrar respostas enviadas
    if "CÓDIGO" not in df_respostas.columns:
        st.error("❌ A planilha de respostas está sem o cabeçalho correto.")
        st.stop()

    respostas_do_codigo = df_respostas[df_respostas["CÓDIGO"].str.upper() == codigo]

    if respostas_do_codigo.empty:
        st.info("📭 Nenhuma resposta foi enviada ainda para este código.")
    else:
        st.markdown("### 👨‍🏫 Alunos que realizaram a atividade:")
        for _, row in respostas_do_codigo.iterrows():
            st.markdown(f"#### 👤 {row['NOME']} - {row['ESCOLA']} ({row['TURMA']})")
            col1, col2 = st.columns([3, 1])
            with col1:
                respostas_html = ""
                for i in range(5, len(row), 2):
                    atividade = row[i]
                    resposta = row[i+1] if i+1 < len(row) else "?"
                    gabarito_row = df_gabarito[df_gabarito["ATIVIDADE"] == atividade]
                    gabarito = gabarito_row["GABARITO"].values[0] if not gabarito_row.empty else "?"
                    respostas_html += f"<li><strong>{atividade}</strong>: Resposta: {resposta} | Gabarito: {gabarito}</li>"
                st.markdown(f"<ul>{respostas_html}</ul>", unsafe_allow_html=True)
