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

codigo = st.text_input("🔍 Inserir Código Desejado:").strip().upper()

if codigo:
    st.markdown("---")
    st.markdown(f"### 🧾 Detalhes do código: `{codigo}`")

    df_geradas = carregar_dados("ATIVIDADES_GERADAS!A1:Z", has_header=True)
    df_respostas = carregar_dados("ATIVIDADES!A1:Z", has_header=True)
    df_gabarito = carregar_dados("MATEMATICA!A1:M", has_header=True)

    atividades_do_codigo = df_geradas[df_geradas["CODIGO"] == codigo]
    if atividades_do_codigo.empty:
        st.warning("❗ Código não encontrado na base de atividades geradas.")
        st.stop()

    atividade_cols = [col for col in df_geradas.columns if col.startswith("ATIVIDADE")]
    atividades_escolhidas = atividades_do_codigo[atividade_cols].values.flatten().tolist()
    atividades_escolhidas = [a for a in atividades_escolhidas if a]

    if "CODIGO" not in df_respostas.columns:
        st.error("❌ A planilha de respostas está sem o cabeçalho correto.")
        st.stop()

    respostas_do_codigo = df_respostas[df_respostas["CODIGO"].str.upper() == codigo]

    if respostas_do_codigo.empty:
        st.info("📭 Nenhuma resposta foi enviada ainda para este código.")
    else:
        gabaritos_dict = {}
        for atividade in atividades_escolhidas:
            linha = df_gabarito[df_gabarito["ATIVIDADE"] == atividade]
            if not linha.empty:
                gabaritos_dict[atividade] = linha.iloc[0]["GABARITO"]
            else:
                gabaritos_dict[atividade] = "?"

        st.markdown("### ✅ Atividades Escolhidas pelo Professor:")
        col1, col2 = st.columns(2)
        for i, nome in enumerate(atividades_escolhidas):
            gabarito = gabaritos_dict.get(nome, "?")
            col = col1 if i % 2 == 0 else col2
            col.markdown(f"**{i+1}. {nome}** - Gabarito: **{gabarito}**")

        st.markdown("### 👨‍🏫 Alunos que realizaram a atividade:")
        grupos = respostas_do_codigo.groupby(["ESCOLA", "TURMA"])
        for (escola, turma), grupo in grupos:
            st.markdown(f"**🏫 {escola}** - **Turma: {turma}**")
            for _, row in grupo.iterrows():
                nome = row["NOME"]
                acertos = 0
                total = 0
                linha_resumo = ""
                for i in range(5, len(row), 3):
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

                st.markdown(f"<b>{nome}</b> <span style='font-size:12px;'> - {acertos}/{total} acertos</span>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-size:11px;'>{linha_resumo}</div>", unsafe_allow_html=True)
            st.markdown("---")
else:
    st.info("✏️ **Insira o código da atividade e tecle ENTER** para visualizar os dados.")