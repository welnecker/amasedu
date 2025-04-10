import streamlit as st
import pandas as pd
import random
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

st.set_page_config(page_title="Relatórios AMA 2025", page_icon="📊")

st.markdown("""
    <style>
    /* Centraliza e limita a largura do container principal */
    .appview-container .main .block-container {
        max-width: 1000px;
        margin-left: auto;
        margin-right: auto;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    /* Opcional: ajusta a largura da barra lateral */
    section[data-testid="stSidebar"] {
        width: 250px !important;
    }

    /* Garante que botões não fiquem colados no campo */
    button[kind="secondary"] {
        margin-top: 1.75rem;
    }
    </style>
""", unsafe_allow_html=True)


# --- Autenticação por senha ---
# --- Autenticação por e-mail institucional ---
if "relatorio_autenticado" not in st.session_state:
    st.session_state.relatorio_autenticado = False

if not st.session_state.relatorio_autenticado:
    st.markdown("### 🔐 Acesso restrito aos professores")

    email = st.text_input("Digite seu e-mail institucional:")

    if email.endswith("@educador.edu.es.gov.br"):
        st.session_state.relatorio_autenticado = True
        st.success("✅ Acesso autorizado!")
        st.rerun()
    elif email:
        st.error("❌ E-mail inválido. Use seu e-mail institucional.")
    st.stop()


# --- Função para carregar dados do Google Sheets ---
@st.cache_data(show_spinner=False)
def carregar_dados(sheet_range, has_header=True, forcar_recarga=False):
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
        data = []
        for row in values[1:]:
            if len(row) < 2 or not row[1].strip():  # Coluna B (índice 1) vazia -> parar
                break
            data.append(row)

        col_count = len(header)
        data_corrigida = []
        for linha in data:
            if len(linha) < col_count:
                linha += [""] * (col_count - len(linha))
            elif len(linha) > col_count:
                linha = linha[:col_count]
            data_corrigida.append(linha)

        return pd.DataFrame(data_corrigida, columns=header)
    else:
        return pd.DataFrame(values)


# --- Interface ---
st.markdown("<h1 style='font-size:28px; white-space:nowrap;'>📊 Relatórios de Atividades - AMA 2025</h1>", unsafe_allow_html=True)
st.markdown("Use o campo abaixo para buscar os dados de um código de atividade:")

col1, col2 = st.columns([4, 1])
with col1:
    codigo_input = st.text_input("🔍 Inserir Código Desejado:", key="codigo_input").strip().upper()
with col2:
    atualizar = st.button("🔄 Atualizar Lista")

if atualizar:
    st.session_state.codigo_busca = codigo_input
    st.session_state.forcar_recarga = random.random()  # força nova versão da função cacheada

codigo = st.session_state.get("codigo_busca", "")

if codigo:
    st.markdown("---")
    st.markdown(f"### 🧾 Detalhes do código: `{codigo}`")

    df_respostas = carregar_dados("ATIVIDADES!A1:AI", has_header=True, forcar_recarga=st.session_state.get("forcar_recarga", 0))

    if "CODIGO" in df_respostas.columns:
        respostas_do_codigo = df_respostas[df_respostas["CODIGO"].fillna("").str.strip().str.upper() == codigo]

        if respostas_do_codigo.empty:
            st.info("📬 Nenhuma resposta foi enviada ainda para este código.")
            st.stop()

        st.markdown("### 👨‍🏫 Alunos que realizaram a atividade:")
        grupos = respostas_do_codigo.groupby(["ESCOLA", "TURMA"])

        for (escola, turma), grupo in grupos:
            st.markdown(f"**🏫 {escola}** - **Turma: {turma}**")
            for _, row in grupo.iterrows():
                nome = row["NOME"]
                acertos = 0
                total = 0
                linha_resumo = ""

                for i in range(5, 35, 3):  # Somente Q1 a Q10 (colunas 5 a 34)
                    q = row[i] if i < len(row) else ""
                    r = row[i+1] if i+1 < len(row) else ""
                    s = row[i+2] if i+2 < len(row) else ""

                    if not q:
                        continue

                    correto = "✔️" if s.strip().lower() == "certo" else "❌"
                    if s.strip().lower() == "certo":
                        acertos += 1
                    total += 1
                    linha_resumo += f"<span style='font-size:12px; white-space:nowrap; margin-right:8px;'><b>{q}</b> ({r}) {correto}</span>"

                st.markdown(f"<b>{nome}</b> <span style='font-size:12px;'> - {acertos}/{total} acertos</span>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-size:11px;'>{linha_resumo}</div>", unsafe_allow_html=True)
            st.markdown("---")
    else:
        st.error("A coluna 'CODIGO' não foi encontrada na planilha.")
else:
    st.info("✏️ **Insira o código da atividade e clique em 'Atualizar Lista' para visualizar os dados.**")
#