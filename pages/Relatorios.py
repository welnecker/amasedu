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

        # Normalizar linhas com número incorreto de colunas
        col_count = len(header)
        data_corrigida = []
        for linha in data:
            if len(linha) < col_count:
                linha += [""] * (col_count - len(linha))  # completa com vazio
            elif len(linha) > col_count:
                linha = linha[:col_count]  # corta excesso
            data_corrigida.append(linha)

        return pd.DataFrame(data_corrigida, columns=header)
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
    
    # Filtrar respostas enviadas
    if "CODIGO" not in df_respostas.columns:
        st.error("❌ A planilha de respostas está sem o cabeçalho correto.")
        st.stop()

    respostas_do_codigo = df_respostas[df_respostas["CODIGO"].str.upper() == codigo]

    if respostas_do_codigo.empty:
        st.info("📭 Nenhuma resposta foi enviada ainda para este código.")
    else:
                # Criar dicionário com os gabaritos escolhidos pelo professor
        # Criar dicionário com os gabaritos escolhidos pelo professor
      gabaritos_dict = {
    atividade: df_gabarito[df_gabarito["ATIVIDADE"] == atividade]["GABARITO"].values[0]
    for atividade in atividades_escolhidas
}

# Exibir atividades escolhidas pelo professor em duas colunas
st.markdown("### ✅ Atividades Escolhidas pelo Professor:")
col1, col2 = st.columns(2)
for i, nome in enumerate(atividades_escolhidas):
    gabarito = gabaritos_dict.get(nome, "?")
    col = col1 if i % 2 == 0 else col2
    col.markdown(f"**{i+1}. {nome}** - Gabarito: **{gabarito}**")

# Exibir respostas por aluno de forma horizontal e compacta
st.markdown("### 👨‍🏫 Alunos que realizaram a atividade:")

for _, row in respostas_do_codigo.iterrows():
    nome = row["NOME"]
    escola = row["ESCOLA"]
    turma = row["TURMA"]

    acertos = 0
    total = 0
    linha_resumo = ""
    for i in range(5, len(row), 3):  # Q, R, S
        q = row[i] if i < len(row) else ""
        r = row[i+1] if i+1 < len(row) else ""
        s = row[i+2] if i+2 < len(row) else ""

        g = gabaritos_dict.get(q, "?")
        correto = "✔️" if s == "Certo" else "❌"
        if s == "Certo":
            acertos += 1
        if q:
            total += 1
        linha_resumo += f"<span style='font-size:12px; white-space:nowrap; margin-right:8px;'><b>{q}</b> ({r}/{g}) {correto}</span>"

    st.markdown(f"<b>{nome} - {escola} ({turma})</b> <span style='font-size:12px;'> - {acertos}/{total} acertos</span>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:11px;'>{linha_resumo}</div>", unsafe_allow_html=True)
    st.markdown("---")


