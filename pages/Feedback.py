import streamlit as st

st.set_page_config(page_title="Feedback AMA 2025", page_icon="📝")

st.title("📝 Envie seu Feedback")

st.markdown("""
Queremos saber como foi sua experiência com o AMA 2025.  
Por favor, preencha o formulário abaixo para nos ajudar a melhorar:

<iframe src="https://docs.google.com/forms/d/e/1FAIpQLSdxICVdcS9nEgH_vwetgvJHZRQEYPDJXCOywaTaNVC4F6XLRQ/viewform?embedded=true" width="100%" height="800" frameborder="0" marginheight="0" marginwidth="0">Carregando…</iframe>
""", unsafe_allow_html=True)
