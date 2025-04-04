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


# --- FUNÇÃO DE CARGA ROBUSTA ---
@st.cache_data
def carregar_dados(range_nome):
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"])
    service = build("sheets", "v4", credentials=creds)

    result = service.spreadsheets().values().get(
        spreadsheetId="17SUODxQqwWOoC9Bns--MmEDEruawdeEZzNXuwh3ZIj8",
        range=range_nome
    ).execute()

    values = result.get("values", [])
    if not values or len(values) < 2:
        return pd.DataFrame()

    headers = values[0]
    max_len = max(len(row) for row in values[1:])
    if len(headers) < max_len:
        headers += [f"EXTRA_{i}" for i in range(len(headers), max_len)]

    data = [row + [None] * (len(headers) - len(row)) for row in values[1:]]
    return pd.DataFrame(data, columns=headers)


# --- INTERFACE ---
st.title("📊 Relatórios de Atividades - AMA 2025")
st.markdown("Use o campo abaixo para buscar os dados de um código de atividade:")

codigo = st.text_input("🔍 Inserir Código Desejado:").strip().upper()

if codigo:
    st.markdown("---")
    st.markdown(f"### 🧾 Detalhes do código: `{codigo}`")

    df_geradas = carregar_dados("ATIVIDADES_GERADAS!A1:Z")
    df_respostas = carregar_dados("ATIVIDADES!A1:Z")
    df_gabarito = carregar_dados("MATEMATICA!A1:N")

    atividades_do_codigo = df_geradas[df_geradas["CODIGO"] == codigo]
    respostas_do_codigo = df_respostas[df_respostas["CODIGO"].str.upper() == codigo]

    if atividades_do_codigo.empty:
        st.warning("❗ Código não encontrado na base de atividades geradas.")
        st.stop()

    # Atividades escolhidas
    st.subheader("✅ Atividades Escolhidas pelo Professor:")
    atividades_escolhidas = [x for x in atividades_do_codigo.values[0][2:] if x]
    for i, nome in enumerate(atividades_escolhidas, 1):
        gabarito = df_gabarito[df_gabarito["ATIVIDADE"] == nome]["GABARITO"]
        gab = gabarito.values[0] if not gabarito.empty else "?"
        st.markdown(f"{i}. **{nome}** — Gabarito: `{gab}`")

    # Respostas
    if respostas_do_codigo.empty:
        st.info("Nenhuma resposta foi enviada ainda para este código.")
        st.stop()

    st.subheader("📋 Respostas dos Alunos:")
    for idx, row in respostas_do_codigo.iterrows():
        nome = row["NOME"]
        escola = row["ESCOLA"]
        turma = row["TURMA"]

        st.markdown(f"#### 👤 {nome} — {escola} ({turma})")
        respostas_html = ""

        acertos = 0
        for i in range(5, len(row), 2):
            atividade = row[i]
            resposta = row[i + 1] if i + 1 < len(row) else "?"

            if pd.isna(atividade):
                continue

            gabarito_row = df_gabarito[df_gabarito["ATIVIDADE"] == atividade]
            gabarito = gabarito_row["GABARITO"].values[0] if not gabarito_row.empty else "?"

            status = "✅" if resposta.upper() == gabarito else "❌"
            if status == "✅":
                acertos += 1

            respostas_html += f"<li>{atividade}: Resposta: <strong>{resposta}</strong> {status}</li>"

        st.markdown(f"<ul>{respostas_html}</ul>", unsafe_allow_html=True)
        st.info(f"🟢 Total de acertos: **{acertos}/{len(atividades_escolhidas)}**")
