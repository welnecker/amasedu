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

# --- FUNÇÃO PARA CARREGAR PLANILHA ---
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
    data = [row + [None] * (len(headers) - len(row)) for row in values[1:]]
    return pd.DataFrame(data, columns=headers)

# --- INTERFACE ---
st.title("📊 Relatórios de Atividades - AMA 2025")
codigo = st.text_input("🔍 Inserir Código Desejado:").strip().upper()

if codigo:
    st.markdown("---")
    st.markdown(f"### 🧾 Detalhes do código: `{codigo}`")

    # Carrega dados
    df_geradas = carregar_dados("ATIVIDADES_GERADAS!A1:Z")
    df_respostas = carregar_dados("ATIVIDADES!A1:Z")
    df_gabarito = carregar_dados("MATEMATICA!A1:N")

    # Normaliza colunas
    for col in ["CÓDIGO", "CODIGO"]:
        if col in df_geradas.columns:
            df_geradas["CODIGO"] = df_geradas[col].astype(str).str.strip().str.upper()
            break

    if "CÓDIGO" not in df_respostas.columns:
        st.warning("❌ A coluna CÓDIGO não está presente nas respostas.")
        st.stop()

    atividades_professor = df_geradas[df_geradas["CODIGO"] == codigo]
    respostas_codigo = df_respostas[df_respostas["CÓDIGO"] == codigo]

    if atividades_professor.empty:
        st.warning("❌ Código não encontrado na base de atividades geradas.")
        st.stop()

    st.subheader("✅ Atividades Escolhidas pelo Professor:")

    atividades_listadas = [item for item in atividades_professor.iloc[0].values[2:] if item]
    for ativ in atividades_listadas:
        gabarito_match = df_gabarito[df_gabarito["ATIVIDADE"] == ativ]
        gabarito = gabarito_match["GABARITO"].values[0] if not gabarito_match.empty else "?"
        st.markdown(f"🔹 **{ativ}** — Gabarito: `{gabarito}`")

    if respostas_codigo.empty:
        st.info("⚠️ Nenhuma resposta foi enviada ainda para este código.")
        st.stop()

    st.markdown("### 👩‍🎓 Alunos que realizaram a atividade:")

    for _, aluno in respostas_codigo.iterrows():
        nome = aluno["NOME"]
        escola = aluno["ESCOLA"]
        turma = aluno["TURMA"]
        st.markdown(f"#### 👤 {nome} — {escola} ({turma})")

        respostas_html = "<ul>"
        acertos = 0
        total = 0

        for i in range(5, len(aluno), 2):
            atividade = aluno[i]
            resposta = aluno[i + 1] if i + 1 < len(aluno) else "?"
            if not atividade:
                continue

            gabarito_row = df_gabarito[df_gabarito["ATIVIDADE"] == atividade]
            gabarito = gabarito_row["GABARITO"].values[0] if not gabarito_row.empty else "?"

            correto = resposta.upper() == gabarito
            icone = "✅" if correto else "❌"
            if correto:
                acertos += 1
            total += 1

            respostas_html += f"<li>{icone} <strong>{atividade}</strong>: Resposta = {resposta}, Gabarito = {gabarito}</li>"

        respostas_html += "</ul>"
        st.markdown(f"Acertos: **{acertos}/{total}**", unsafe_allow_html=True)
        st.markdown(respostas_html, unsafe_allow_html=True)
        st.markdown("---")
