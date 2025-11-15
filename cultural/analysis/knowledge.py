from pathlib import Path
import json
import logging
from .constants import MAX_FEWSHOT_EJEMPLOS

logger = logging.getLogger(__name__)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_FILE = DATA_DIR / "elementos_huanuco.json"

def load_verified_elements() -> list:
    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("Archivo elementos_huanuco.json no encontrado en cultural/data/")
        return []
    except Exception as e:
        logger.error(f"Error leyendo elementos verificados: {e}")
        return []

def get_hardcoded_examples() -> str:
    return """
        GASTRONOMÍA:
        - Pachamanca Huanuqueña (Confianza: 0.90)
            Descripción: Técnica ancestral de cocción bajo tierra con piedras calientes...
            Ubicación: Toda la región de Huánuco
            Periodo: Preincaico hasta la actualidad

        PATRIMONIO ARQUEOLÓGICO:
        - Kotosh - Templo de las Manos Cruzadas (Confianza: 0.95)
            Descripción: Sitio arqueológico de 4000 años de antigüedad...
            Ubicación: Distrito de Kotosh, 5 km de Huánuco
            Periodo: Precerámico (2000–1500 a.C.)
        """

def load_cultural_examples(num_examples: int = MAX_FEWSHOT_EJEMPLOS) -> str:
    elementos = load_verified_elements()
    if not elementos:
        return get_hardcoded_examples()

    # 2–3 por categoría
    ejemplos_por_cat = {}
    for e in elementos:
        cat = e.get("categoria", "General")
        ejemplos_por_cat.setdefault(cat, [])
        if len(ejemplos_por_cat[cat]) < 3:
            ejemplos_por_cat[cat].append(e)

    bloques, count = [], 0
    for cat, items in ejemplos_por_cat.items():
        if count >= num_examples: break
        bloques.append(f"\n{cat}:")
        for it in items:
            if count >= num_examples: break
            conf = float(it.get("confianza", 0.8))
            bloques.append(
                f"""  - {it.get('titulo','(sin título)')} (Confianza esperada: {conf:.2f})
                Descripción: {it.get('descripcion','')[:180]}...
                Ubicación: {it.get('ubicacion','')}
                Periodo: {it.get('periodo_historico','')}"""
            )
            count += 1

    return "\n".join(bloques) if bloques else get_hardcoded_examples()
