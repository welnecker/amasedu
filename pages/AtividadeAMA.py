import streamlit as st
import pandas as pd
import requests
from io import StringIO
import fitz
from PIL import Image
from io import BytesIO
import urllib.request
from datetime import datetime

st.set_page_config(page_title="ATIVIDADE AMA 2025", page_icon="📚")

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

st.subheader("Preencha o cabeçalho da atividade:")
titulo_escola = st.text_input("Escola:")
data = st.date_input("Data:")
nome_professor = st.text_input("Nome do Professor(a):")

if "atividades_exibidas" not in st.session_state or len(st.session_state["atividades_exibidas"]) == 0:
    st.warning("Nenhuma atividade selecionada. Volte e escolha as atividades.")
else:
    imagens_baixadas = False
    erro_download = False

    st.success("Atividades selecionadas:")
    col_a, col_b = st.columns(2)
    for i, idx in enumerate(st.session_state.atividades_exibidas):
        nome = dados.loc[idx, "ATIVIDADE"]
        with (col_a if i % 2 == 0 else col_b):
            st.markdown(f"- **Atividade:** {nome}")

    col_gerar, col_cancelar, col_proxy = st.columns([1, 1, 1])
    with col_gerar:
        if st.button("📄 GERAR ATIVIDADE"):
            with st.spinner("Inserindo imagens no PDF existente..."):
                pdf_path = "modelo.pdf"
                pdf_document = fitz.open(pdf_path)

                first_page = pdf_document[0]
                y_position = 120

                text = (
                    f"Escola: {titulo_escola}                       Data: {data.strftime('%d/%m/%Y')}\n"
                    f"Estudante: _________________________________     Turma: ____________\n"
                    f"Professor(a): {nome_professor}"
                )

                first_page.insert_text(
                    fitz.Point(72, y_position),
                    text,
                    fontsize=12,
                    fontname="helv",
                    color=(0, 0, 0),
                )

                y_position += 60
                page = first_page

                for idx in st.session_state.atividades_exibidas:
                    nome_atividade = dados.loc[idx, "ATIVIDADE"]
                    url_img = f"https://questoesama.pages.dev/{nome_atividade}.jpg"

                    try:
                        req = urllib.request.Request(
                            url_img,
                            headers={'User-Agent': 'Mozilla/5.0'}
                        )
                        with urllib.request.urlopen(req) as resp:
                            img = Image.open(BytesIO(resp.read())).convert("RGB")

                        imagens_baixadas = True

                        img_bytes = BytesIO()
                        img.save(img_bytes, format='JPEG')

                        if y_position > 700:
                            page = pdf_document.new_page()
                            y_position = 10

                        page.insert_image(fitz.Rect(72, y_position, 520, y_position + 160), stream=img_bytes.getvalue())
                        y_position += 162

                    except Exception as e:
                        erro_download = True

                if erro_download:
                    st.warning("⚠️ Algumas imagens não foram baixadas. Verifique sua conexão.")

                if imagens_baixadas:
                    pdf_bytes = pdf_document.write()
                    nome_arquivo = f"{nome_professor}_{data.strftime('%Y-%m-%d')}.pdf"
                    st.download_button("📥 Baixar PDF Completo", pdf_bytes, nome_arquivo, "application/pdf")
                    st.success("PDF criado com sucesso!")

        if st.button("❌ CANCELAR E RECOMEÇAR"):
            st.session_state.clear()
            st.switch_page("QuestoesAMA.py")

        if st.button("⚙️ Configurar Proxy"):
            st.switch_page("pages/Proxy.py")

    st.markdown("<hr />", unsafe_allow_html=True)
    st.success("Links das atividades selecionadas:")
    col1, col2 = st.columns(2)
    for count, idx in enumerate(st.session_state.atividades_exibidas):
        nome = dados.loc[idx, "ATIVIDADE"]
        url_img = f"https://questoesama.pages.dev/{nome}.jpg"
        with col1 if count % 2 == 0 else col2:
            st.markdown(f"[{nome}]({url_img}) - Visualize esta atividade.")
