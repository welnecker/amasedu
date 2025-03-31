# 📚 ATIVIDADE AMA 2025

Aplicativo web desenvolvido em **Streamlit** para geração de atividades educacionais em formato PDF, utilizando colagens de imagens pré-definidas. Idealizado para facilitar o trabalho de professores da rede AMA com foco em habilidades, descritores e níveis de dificuldade.

---

## 🚀 Funcionalidades

- 📑 Filtro por Série, Habilidade e Descritor
- ✅ Seleção de até 10 atividades por vez
- 🧩 Organização por níveis: Fácil, Médio e Difícil
- ✍️ Preenchimento de cabeçalho personalizado (Escola, Data, Professor)
- 🖼️ Inserção automática de imagens no PDF
- 📥 Download automático do PDF final

---

## 🔗 Acesse agora

👉 [Clique aqui para usar o app](https://amasedu-rgfmpcgtzertvpnjyicqfz.streamlit.app/)

---

## 🖼️ Exemplo visual

| Filtro de Atividades | Geração do PDF |
|----------------------|----------------|
| ![](https://raw.githubusercontent.com/seu-usuario/seu-repo/main/exemplo1.png) | ![](https://raw.githubusercontent.com/seu-usuario/seu-repo/main/exemplo2.png) |

---

## 🛠️ Como rodar localmente

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/seu-repo.git
cd seu-repo

# Crie ambiente virtual (opcional)
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\\Scripts\\activate   # Windows

# Instale as dependências
pip install -r requirements.txt

# Rode o app
streamlit run app.py

📦 projeto/
├── app.py               # Página inicial (filtros e seleção)
├── pages/
│   └── AtividadeAMA.py  # Página de geração do PDF
├── modelo.pdf           # Modelo base usado para inserir imagens
├── requirements.txt     # Lista de dependências
└── README.md



⚙️ Tecnologias utilizadas
Streamlit

Pandas

PyMuPDF (fitz)

Pillow

Google Sheets (como backend de dados)

GitHub Pages / Cloudflare Pages (para hospedar imagens)

📌 Observações
O app utiliza um modelo de PDF (modelo.pdf) como base.

As imagens das atividades devem estar publicadas no repositório: https://questoesama.pages.dev/

O limite de seleção é de 10 atividades por vez.

🧑‍🏫 Público-alvo
Professores da rede AMA que precisam gerar atividades pedagógicas diárias de forma rápida, com base em habilidades e descritores específicos.

📄 Licença
Este projeto está licenciado sob a MIT License.



