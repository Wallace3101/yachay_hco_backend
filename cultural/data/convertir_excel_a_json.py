# convertir_excel_a_json.py (ejecútalo una vez)
import os, json, pandas as pd
from datetime import datetime

BASE = os.path.dirname(__file__)
df = pd.read_excel(os.path.join(BASE, "elementos_huanuco.xlsx"))

# Asegúrate de que las columnas coincidan con estos nombres
esperadas = [
    "titulo","categoria","confianza","descripcion",
    "contexto_cultural","periodo_historico","ubicacion","significado"
]
faltan = [c for c in esperadas if c not in df.columns]
if faltan:
    raise SystemExit(f"Faltan columnas en Excel: {faltan}")

# Función para convertir objetos datetime a string
def convertir_fechas(obj):
    if isinstance(obj, datetime):
        return obj.strftime("%Y-%m-%d")  # Convierte a formato fecha
    return obj

# Convertir DataFrame a diccionario y procesar fechas
elementos = []
for _, row in df.iterrows():
    elemento = {}
    for columna in esperadas:
        valor = row[columna]
        # Convertir datetime a string
        if isinstance(valor, datetime):
            elemento[columna] = valor.strftime("%Y-%m-%d")
        elif pd.isna(valor):  # Manejar valores NaN
            elemento[columna] = None
        else:
            elemento[columna] = valor
    elementos.append(elemento)

dest_dir = os.path.join(BASE, "api", "cultural", "data")
os.makedirs(dest_dir, exist_ok=True)
dest = os.path.join(dest_dir, "elementos_huanuco.json")

with open(dest, "w", encoding="utf-8") as f:
    json.dump(elementos, f, ensure_ascii=False, indent=2)

print(f"OK -> {dest} ({len(elementos)} registros)")