import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os

# Caminho da planilha de entrada
caminho_planilha = r"C:\Users\jdwelnecker\Desktop\AMA2025\Planilhaquestoes\questoes.xlsx"

# Caminho da pasta onde as imagens serão salvas
pasta_saida = r"C:\Users\jdwelnecker\Desktop\AMA2025\Planilhaquestoes\questoesprontas"
os.makedirs(pasta_saida, exist_ok=True)

# Lê a planilha (use a primeira aba ou especifique sheet_name="nome")
df = pd.read_excel(caminho_planilha)

# Extrai os nomes únicos da coluna "ATIVIDADE"
nomes_atividades = df["ATIVIDADE"].dropna().unique().tolist()

# Fonte
try:
    fonte = ImageFont.truetype("arial.ttf", 42)
except:
    fonte = ImageFont.load_default()

# Geração das imagens
for nome in nomes_atividades:
    nome = nome.strip()
    img = Image.new("RGB", (800, 600), color="white")
    draw = ImageDraw.Draw(img)

    bbox = draw.textbbox((0, 0), nome, font=fonte)
    largura_texto = bbox[2] - bbox[0]
    altura_texto = bbox[3] - bbox[1]
    pos_x = (800 - largura_texto) // 2
    pos_y = (600 - altura_texto) // 2
    draw.text((pos_x, pos_y), nome, fill="black", font=fonte)


    caminho_imagem = os.path.join(pasta_saida, f"{nome}.jpg")
    img.save(caminho_imagem)

print("✅ Imagens salvas em:", pasta_saida)
