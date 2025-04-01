import requests
from urllib.parse import urlencode

url = "https://docs.google.com/forms/d/e/1FAIpQLSdxICVdcS9nEgH_vwetgvJHZRQEYPDJXCOywaTaNVC4F6XLRQ/formResponse"

dados = {
    "entry.1932539975": "EEEFM ARISTÓBULO BARBOSA LEÃO",  # Escola
    "entry.1534567646": "JANIO DONISETE WELNECKER",        # Professor
    "entry.272957323": "9º ANO",                            # Série
    "entry.465063798": "D05",                               # Descritor
    "entry.537108716": "EF09MA16",                          # Habilidade
    "entry.633190190": "5"                                  # Total de questões
}

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "https://docs.google.com/forms/d/e/1FAIpQLSdxICVdcS9nEgH_vwetgvJHZRQEYPDJXCOywaTaNVC4F6XLRQ/viewform",
    "User-Agent": "Mozilla/5.0"
}

response = requests.post(url, data=urlencode(dados), headers=headers)
print("Status:", response.status_code)
print("Resposta:", response.text)
