from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
import fitz  # PyMuPDF
from PIL import Image
import urllib.request
from io import BytesIO
from datetime import datetime
import pandas as pd

app = FastAPI()

class PDFRequest(BaseModel):
    escola: str
    professor: str
    data: str  # formato: "YYYY-MM-DD"
    atividades: List[str]
    titulo: str = "ATIVIDADE"

# Função auxiliar para buscar o gabarito correto da atividade

def buscar_gabarito(atividades: List[str]) -> List[str]:
    try:
        # Planilha compartilhada com abas MATEMATICA e PORTUGUES
        url_mat = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQhv1IMZCz0xYYNGiEIlrqzvsELrjozHr32CNYHdcHzVqYWwDUFolet_2XOxv4EX7Tu3vxOB4w-YUX9/pub?gid=2127889637&single=true&output=csv"
        url_por = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQhv1IMZCz0xYYNGiEIlrqzvsELrjozHr32CNYHdcHzVqYWwDUFolet_2XOxv4EX7Tu3vxOB4w-YUX9/pub?gid=1217179376&single=true&output=csv"

        df_mat = pd.read_csv(url_mat)
        df_por = pd.read_csv(url_por)
        df = pd.concat([df_mat, df_por], ignore_index=True)

        df["ATIVIDADE"] = df["ATIVIDADE"].astype(str).str.strip()
        df["GABARITO"] = df["GABARITO"].astype(str).str.strip().str.upper()

        lista = []
        for i, atividade in enumerate(atividades, start=1):
            letra = df[df["ATIVIDADE"] == atividade]["GABARITO"].values
            if letra.any():
                lista.append(f"{i} - {letra[0]}")
            else:
                lista.append(f"{i} - ?")

        return lista

    except:
        return [f"{i} - ?" for i in range(1, len(atividades)+1)]


@app.post("/gerar-pdf")
async def gerar_pdf(req: PDFRequest):
    try:
        pdf = fitz.open("modelo.pdf")
        pagina = pdf[0]

        # Cabeçalho
        y_base = 100
        pagina.insert_text(fitz.Point(72, y_base),
                           f"Escola: {req.escola}    Data: {datetime.strptime(req.data, '%Y-%m-%d').strftime('%d/%m/%Y')}",
                           fontsize=12, fontname="helv", color=(0, 0, 0))
        pagina.insert_text(fitz.Point(72, y_base + 20),
                           "Estudante: _________________________________    Turma: ____________",
                           fontsize=12, fontname="helv", color=(0, 0, 0))
        pagina.insert_text(fitz.Point(72, y_base + 40),
                           f"Professor(a): {req.professor}",
                           fontsize=12, fontname="helv", color=(0, 0, 0))

        # Título centralizado
        titulo_texto = req.titulo.upper()
        largura_titulo = fitz.get_text_length(titulo_texto, fontname="helv", fontsize=14)
        pagina_largura = pagina.rect.width
        posicao_x = (pagina_largura - largura_titulo) / 2
        pagina.insert_text(fitz.Point(posicao_x, 160),
                           titulo_texto, fontsize=14, fontname="helv", color=(0, 0, 0))

        # Imagens
        y = 185
        for i, nome in enumerate(req.atividades, start=1):
            url_img = f"https://questoesama.pages.dev/{nome}.jpg"
            try:
                req_img = urllib.request.Request(url_img, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req_img) as resp:
                    img = Image.open(BytesIO(resp.read())).convert("RGB")
                    buffer = BytesIO()
                    img.save(buffer, format='JPEG')

                    if y > 700:
                        pagina = pdf.new_page()
                        y = 50
                    else:
                        y += 12

                    pagina.insert_text(fitz.Point(72, y), f"Questão {i}", fontsize=12, fontname="helv", color=(0, 0, 0))
                    y += 22

                    pagina.insert_image(
                        fitz.Rect(72, y, 520, y + 160),
                        stream=buffer.getvalue()
                    )
                    y += 162
            except:
                continue

        # Insere imagem do gabarito em branco
        pagina = pdf.new_page()
        try:
            url_gabarito = "https://questoesama.pages.dev/img/gabarito-preencher.jpg"
            req_img = urllib.request.Request(url_gabarito, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req_img) as resp:
                img = Image.open(BytesIO(resp.read())).convert("RGB")
                buffer = BytesIO()
                img.save(buffer, format='JPEG')

                pagina.insert_image(fitz.Rect(72, 60, 520, 760), stream=buffer.getvalue())
        except:
            pass

        # Insere gabarito correto como texto na página seguinte
        gabarito_lista = buscar_gabarito(req.atividades)
        pagina = pdf.new_page()
        pagina.insert_text(fitz.Point(72, 60), "GABARITO", fontsize=14, fontname="helv", color=(0, 0, 0))

        for idx, linha in enumerate(gabarito_lista):
            pagina.insert_text(fitz.Point(72, 90 + idx * 20), linha, fontsize=12, fontname="helv", color=(0, 0, 0))

        pdf_bytes = pdf.write()
        pdf_stream = BytesIO(pdf_bytes)
        nome_arquivo = f"{req.professor}_{req.data}.pdf"

        return StreamingResponse(pdf_stream, media_type="application/pdf", headers={
            "Content-Disposition": f"attachment; filename={nome_arquivo}"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))