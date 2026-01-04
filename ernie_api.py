import requests
from pathlib import Path
import os
import json
import re

API_URL = "https://aistudio.baidu.com/llm/lmapi/v3/chat/completions"
TOKEN = ""

def ernie_api():
    md_path = Path("output/output.txt")
    if not md_path.exists():
        raise FileNotFoundError("No se encontró output/output.txt")

    md_text = md_path.read_text(encoding="utf-8")

    prompt = f"""
Convierte el siguiente markdown en una página web HTML moderna y con bastante diseño acorde al Markdown piensa bastante en la estetica de la pagina,
el html y el css se guardan en el mismo directorio asegurate de que siempre funcionen, Ademas asegurate de siempre poner una marca de agua de ERNIE y PaddleOCR-VL
con los siguientes linkes
PaddleOCR-VL: https://github.com/PaddlePaddle/PaddleOCR
ERNIE: https://huggingface.co/BAIDU
Devuelve solo un JSON con dos campos: "html" y "css".

Markdown:
{md_text}
"""

    headers = {
        "Authorization": f"token {TOKEN}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "ernie-3.5-8k",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    print("Enviando markdown a ERNIE…")
    response = requests.post(API_URL, json=body, headers=headers)

    if response.status_code != 200:
        print("Error en la API:")
        print(response.text)
        return

    data = response.json()

    try:
        content = data["choices"][0]["message"]["content"]
    except:
        print("Estructura inesperada:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    cleaned = re.sub(r"```json|```", "", content).strip()

    try:
        json_data = json.loads(cleaned)
    except json.JSONDecodeError:
        print("JSON inválido:")
        print(cleaned)
        return

    html = json_data.get("html", "")
    css = json_data.get("css", "")

    os.makedirs("site", exist_ok=True)
    Path("site/index.html").write_text(html, encoding="utf-8")
    Path("site/styles.css").write_text(css, encoding="utf-8")

    print("Sitio web generado en carpeta: site/")

if __name__ == "__main__":
    ernie_api()

