import json
import logging

logger = logging.getLogger(__name__)

def extract_json(content: str) -> str:
    content = content.replace('```json', '').replace('```', '').strip()
    i, j = content.find('{'), content.rfind('}') + 1
    if i == -1 or j <= i:
        raise ValueError("No se encontró JSON válido en la respuesta")
    return content[i:j]

def normalize_category(category: str) -> str:
    m = {
        'gastronomia': 'GASTRONOMIA', 'gastronomía': 'GASTRONOMIA',
        'patrimonio arqueologico': 'PATRIMONIO_ARQUEOLOGICO',
        'patrimonio arqueológico': 'PATRIMONIO_ARQUEOLOGICO',
        'patrimonio': 'PATRIMONIO_ARQUEOLOGICO',
        'arqueologico': 'PATRIMONIO_ARQUEOLOGICO', 'arqueológico': 'PATRIMONIO_ARQUEOLOGICO',
        'flora medicinal': 'FLORA_MEDICINAL', 'flora': 'FLORA_MEDICINAL', 'medicinal': 'FLORA_MEDICINAL',
        'leyendas y tradiciones': 'LEYENDAS_Y_TRADICIONES', 'leyendas': 'LEYENDAS_Y_TRADICIONES', 'tradiciones': 'LEYENDAS_Y_TRADICIONES',
        'festividades': 'FESTIVIDADES', 'festividad': 'FESTIVIDADES',
        'danza': 'DANZA', 'danzas': 'DANZA', 'baile': 'DANZA',
        'musica': 'MUSICA', 'música': 'MUSICA',
        'vestimenta': 'VESTIMENTA', 'vestuario': 'VESTIMENTA', 'traje': 'VESTIMENTA',
        'arte popular': 'ARTE_POPULAR', 'artesania': 'ARTE_POPULAR', 'artesanía': 'ARTE_POPULAR',
        'naturaleza/cultural': 'NATURALEZA_CULTURAL', 'naturaleza': 'NATURALEZA_CULTURAL',
        'otro': 'OTRO', 'otros': 'OTRO',
    }
    key = category.lower().strip()
    return m.get(key, 'OTRO')  # Default a OTRO en vez de GASTRONOMIA

def parse_response(openai_response: dict) -> dict:
    choices = openai_response.get('choices', [])
    if not choices:
        raise ValueError("OpenAI no retornó resultados")

    content = choices[0].get('message', {}).get('content', '')
    if not content:
        raise ValueError("Respuesta vacía de OpenAI")

    json_content = extract_json(content)
    analysis = json.loads(json_content)

    required = ['titulo','categoria','confianza','descripcion','contexto_cultural','periodo_historico','ubicacion','significado']
    missing = [f for f in required if f not in analysis]
    if missing:
        raise ValueError(f"Campos faltantes en respuesta: {missing}")

    if not isinstance(analysis['confianza'], (int, float)) or not (0 <= analysis['confianza'] <= 1):
        raise ValueError("Confianza inválida")

    analysis['categoria'] = normalize_category(analysis['categoria'])
    return analysis
