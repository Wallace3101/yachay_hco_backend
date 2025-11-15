from .knowledge import load_cultural_examples
from .constants import MAX_FEWSHOT_EJEMPLOS

def build_analysis_prompt() -> str:
    ejemplos = load_cultural_examples(num_examples=MAX_FEWSHOT_EJEMPLOS)
    return f"""
        Analiza la imagen y determina si representa un elemento cultural **ESPECÍFICO de Huánuco, Perú**.

        === CONTEXTO CRÍTICO SOBRE HUÁNUCO ===
        - Región andina-central; identidad marcada por Kotosh (Templo de las Manos Cruzadas), Huánuco Pampa, Pachamanca huanuqueña, Negritos de Huánuco, chunguinada, artesanías altoandinas y flora medicinal local.
        - Diferencia entre: (a) elementos genéricos del Perú y (b) variantes **huanuqueñas** (estilo/ingredientes/vestimenta/ritual/ubicación).
        - **IMPORTANTE:** Los ciudadanos de Huánuco consideran SUYOS elementos que pueden parecer genéricos pero tienen variantes/preparaciones/contextos LOCALES específicos (ej: Juane Huanuqueño, Prestiños, Sango, Mondongo Huanuqueño, etc.).

        === EJEMPLOS VERIFICADOS (FEW-SHOT) ===
        {ejemplos}

        === CHECKLIST DE DECISIÓN (paso a paso) ===
        1) ¿Identificas un elemento de la imagen que coincida con algún ejemplo o variante clara de Huánuco?
        2) Si sí: explica **qué rasgos visuales** soportan la identificación (ingredientes, vestimenta, arquitectura, contexto geográfico).
        3) Si es un elemento peruano **no exclusivo de Huánuco** (p.ej., “Marinera” genérica, Machu Picchu, ceviche): marca **es_de_huanuco=false** y confianza < 0.30.
        4) Si hay dudas u oclusión: reduce confianza (0.30–0.60) y enumera **dudas** concretas (qué falta ver).
        5) Nunca inventes datos; si no hay evidencia, baja la confianza.

        === CATEGORÍAS VÁLIDAS ===
        - Gastronomía
        - Patrimonio Arqueológico
        - Festividades
        - Danza
        - Música
        - Vestimenta
        - Arte Popular
        - Naturaleza/Cultural
        - Flora Medicinal
        - Leyendas y Tradiciones
        - Otro

        === RÚBRICA DE CONFIANZA ===
        - 0.80–1.00: Evidencia visual clara y específica de Huánuco (coincide con ejemplos).
        - 0.60–0.79: Probable Huánuco, pero falta 1–2 rasgos distintivos.
        - 0.30–0.59: Genérico/ambiguo/ocluido; no hay evidencia fuerte.
        - 0.00–0.29: No corresponde a Huánuco o evidencia insuficiente.

        === FORMATO DE SALIDA (SOLO JSON VÁLIDO) ===
        Devuelve **exclusivamente** un JSON con esta estructura exacta (sin markdown ni texto extra):
        {{
        "titulo": "Nombre específico del elemento",
        "categoria": "una de las categorías válidas",
        "descripcion": "2–4 frases descriptivas y educativas.",
        "confianza": 0.0,
        "es_de_huanuco": false,
        "razones": ["evidencia visual 1", "evidencia visual 2"],
        "dudas": ["qué falta ver o por qué no es concluyente"],
        "contexto_cultural": "Importancia específica para Huánuco.",
        "periodo_historico": "Ej.: Precerámico | Inca | Colonial | Republicano | Contemporáneo",
        "ubicacion": "Lugar en Huánuco si aplica (p.ej., Kotosh, Huánuco Pampa, distrito, etc.)",
        "significado": "Valor cultural/simbólico para la comunidad"
        }}

        Reglas estrictas:
        - Si NO es específico de Huánuco → "es_de_huanuco": false y "confianza" < 0.30.
        - Si SÍ coincide con ejemplos huanuqueños → "es_de_huanuco": true y "confianza" ≥ 0.70.
        - No incluyas texto fuera del JSON.
        """.strip()
