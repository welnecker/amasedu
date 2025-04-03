import streamlit as st

st.set_page_config(page_title="Bem-vindo ao AMA 2025", page_icon="💡")

st.markdown("<h1 style='text-align: center;'>💡 Bem-vindo ao AMA 2025!</h1>", unsafe_allow_html=True)

st.markdown("---")

st.markdown("""
### 👩‍🏫 Professor(a):

➡️ Inicie clicando em **QuestoesAMA** no menu lateral para montar sua atividade.

### 👨‍🎓 Estudante:

➡️ Acesse a atividade clicando em **AtividadeOnline** no menu lateral e insira o código fornecido pelo(a) professor(a).

---
""")

st.info("Em caso de dúvidas, entre em contato com a coordenação pedagógica.")
