import os
import base64
import requests
import json  

API_URL = "https://lbfdk7jecaaep333.aistudio-app.com/ocr"
TOKEN = "0633dbcbb9d60e0d2cc252429c83bab34993a0df"

file_path = "industria_aeroespacial.pdf"  
input_filename = os.path.splitext(os.path.basename(file_path))[0]
OUTPUT_DIR = "output"

os.makedirs(OUTPUT_DIR, exist_ok=True)

if not os.path.exists(file_path):
    print("Archivo no encontrado:", file_path)
    exit()

with open(file_path, "rb") as file:
    file_bytes = file.read()
    file_data = base64.b64encode(file_bytes).decode("ascii")

headers = {
    "Authorization": f"token {TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "file": file_data,
    "fileType": 0,  
    "useDocOrientationClassify": False,
    "useDocUnwarping": False,
    "useTextlineOrientation": False,
}

print("Enviando archivo a la API...")

response = requests.post(API_URL, json=payload, headers=headers)

if response.status_code != 200:
    print("Error HTTP:", response.status_code)
    print("Respuesta completa:")
    print(response.text)
    exit()

data = response.json()
if "result" not in data:
    print("❌ La API respondió pero no devolvió 'result'")
    print(data)
    exit()

result = data["result"]
all_extracted_text = [] 
full_output_json = []  


# === Procesar OCR ===
for i, res in enumerate(result.get("ocrResults", []), start=1):
    print(f"\n---- Página {i} ----")
    
    pruned_result = res.get("prunedResult", {})

    rec_texts = pruned_result.get("rec_texts", [])
    
    pagina_texto_limpio = "\n".join(rec_texts)
    all_extracted_text.append(f"\n\n--- PAGINA {i} ---\n\n{pagina_texto_limpio}")
    
    print(f"Texto Limpio de Página {i}:\n{pagina_texto_limpio[:200]}...")
    
    full_output_json.append(pruned_result)


    image_url = res.get("ocrImage")
    if image_url:
        img = requests.get(image_url)
        if img.status_code == 200:
            filename = f"{OUTPUT_DIR}/{input_filename}_page_{i}.jpg"
            with open(filename, "wb") as f:
                f.write(img.content)
            print("Imagen guardada:", filename)
        else:
            print("No se pudo descargar imagen. HTTP:", img.status_code)


# === Resultados Finales ===
print("\n" + "="*50)

# 1. Guardar todo el texto limpio en un archivo TXT
final_text_content = "".join(all_extracted_text).strip()

# --- CAMBIO AQUÍ: Nombre de archivo fijo ---
txt_filename = f"{OUTPUT_DIR}/output.txt"

with open(txt_filename, "w", encoding="utf-8") as f:
    f.write(final_text_content)

print(f"Todo el texto extraído guardado en: {txt_filename}")

json_filename = f"{OUTPUT_DIR}/output_resultados_detallados.json" 

with open(json_filename, "w", encoding="utf-8") as f:
    json.dump(full_output_json, f, indent=4, ensure_ascii=False)

print(f"Resultados detallados (JSON) guardados en: {json_filename}")
print("Procesamiento completado.")