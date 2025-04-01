import streamlit as st
import requests
from urllib.parse import urlencode
from datetime import datetime
from io import BytesIO
from fpdf import FPDF

st.set_page_config(page_title="Registro de Aula", page_icon="📝")

st.title("Registro de Aula - AMA 2025")

# Inputs do formulário
professor = st.text_input("Professor:")
disciplina = st.text_input("Disciplina:")
curso = st.text_input("Curso:")
turma = st.text_input("Turma:")
periodo = st.text_input("Período:")
data = st.date_input("Data da Aula:", value=datetime.today())
conteudo = st.text_area("Conteúdo ministrado:")
metodologia = st.text_area("Metodologia:")
recursos = st.text_area("Recursos utilizados:")
atividades = st.text_area("Atividades realizadas:")
dificuldades = st.text_area("Dificuldades apresentadas pelos alunos:")
observacoes = st.text_area("Observações:")

# Função de envio para o Google Forms
def enviar_para_google_forms(dados):
    form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdxICVdcS9nEgH_vwetgvJHZRQEYPDJXCOywaTaNVC4F6XLRQ/formResponse"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://docs.google.com/forms/d/e/1FAIpQLSdxICVdcS9nEgH_vwetgvJHZRQEYPDJXCOywaTaNVC4F6XLRQ/viewform",
        "User-Agent": "Mozilla/5.0"
    }
    try:
        payload_encoded = urlencode(dados)
        response = requests.post(form_url, data=payload_encoded, headers=headers, timeout=10)
        if response.status_code == 200:
            st.success("Dados enviados com sucesso para o Google Forms!")
        else:
            st.warning(f"Falha ao enviar dados. Status code: {response.status_code}")
    except Exception as e:
        st.error(f"Erro ao enviar dados para o Google Forms: {str(e)}")

# Função simples para gerar PDF de teste
def gerar_pdf(professor, data, conteudo):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Registro de Aula - {professor}", ln=True)
    pdf.cell(200, 10, txt=f"Data: {data.strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(5)
    pdf.multi_cell(200, 10, txt=f"Conteúdo: {conteudo}")
    buffer = BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()

# Botão principal
if st.button("📄 Registrar Aula e Enviar"):
    if not professor or not conteudo:
        st.warning("Preencha os campos obrigatórios.")
        st.stop()

    with st.spinner("Enviando dados e gerando PDF..."):
        dados_forms = {
            "entry.1368854772": professor,
            "entry.974489804": disciplina,
            "entry.1741252485": curso,
            "entry.1530314189": turma,
            "entry.1606156186": periodo,
            "entry.1307551010": data.strftime("%d/%m/%Y"),
            "entry.1286342616": conteudo,
            "entry.1399428661": metodologia,
            "entry.1770042575": recursos,
            "entry.493596244": atividades,
            "entry.1335884778": dificuldades,
            "entry.839337160": observacoes,
        }

        enviar_para_google_forms(dados_forms)

        pdf_bytes = gerar_pdf(professor, data, conteudo)
        st.download_button(
            label="📥 Baixar PDF do Registro",
            data=pdf_bytes,
            file_name=f"registro_{data.strftime('%Y-%m-%d')}.pdf",
            mime="application/pdf"
        )

        st.success("Registro completo com sucesso!")
