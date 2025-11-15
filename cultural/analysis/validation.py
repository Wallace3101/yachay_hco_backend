"""
Validación mejorada con búsqueda semántica y ajuste dinámico de confianza
"""
from difflib import SequenceMatcher
from typing import Dict, List
from .knowledge import load_verified_elements

def fuzzy_match_score(text1: str, text2: str) -> float:
    """Calcula similitud entre dos textos usando múltiples métricas"""
    # 1. Similitud de secuencia
    seq_sim = SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    # 2. Palabras compartidas (ponderado)
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    if not words1 or not words2:
        return seq_sim
    
    shared = len(words1 & words2)
    total = len(words1 | words2)
    word_sim = shared / total if total > 0 else 0
    
    # 3. Combinación ponderada
    return (seq_sim * 0.6) + (word_sim * 0.4)

def find_best_match(titulo: str, elementos: List[Dict]) -> tuple:
    """Encuentra el mejor match en la base de conocimiento"""
    best_elem = None
    best_score = 0.0
    
    for elem in elementos:
        elem_titulo = elem.get('titulo', '')
        score = fuzzy_match_score(titulo, elem_titulo)
        
        if score > best_score:
            best_score = score
            best_elem = elem
    
    return best_elem, best_score

def adjust_confidence(
    original_conf: float,
    reference_conf: float,
    similarity: float
) -> float:
    """
    Ajusta la confianza basándose en:
    - Confianza original del modelo
    - Confianza del elemento de referencia
    - Similitud del match
    """
    if similarity > 0.85:  # Match muy fuerte
        return max(original_conf, reference_conf)
    elif similarity > 0.70:  # Match fuerte
        return max(original_conf, (original_conf + reference_conf) / 2)
    elif similarity > 0.60:  # Match moderado
        return original_conf * 1.1  # Pequeño boost
    else:
        return original_conf  # Sin cambio

def validate_with_local_knowledge(analysis: dict) -> dict:
    """
    Valida el análisis contra la base de conocimiento local
    y ajusta confianza/descripción si hay match
    """
    elementos = load_verified_elements()
    if not elementos or not analysis:
        return analysis

    titulo = analysis.get('titulo', '')
    if not titulo:
        return analysis

    # Buscar mejor match
    best_elem, similarity = find_best_match(titulo, elementos)
    
    if best_elem and similarity > 0.60:  # Umbral de match
        conf_orig = float(analysis.get('confianza', 0.5))
        conf_ref = float(best_elem.get('confianza', 0.8))
        conf_new = adjust_confidence(conf_orig, conf_ref, similarity)
        
        # Actualizar análisis
        analysis['confianza'] = round(conf_new, 3)
        
        # Agregar metadata de validación
        analysis.setdefault('validacion', {}).update({
            'metodo': 'base_conocimiento_local_v2',
            'elemento_referencia': best_elem.get('titulo'),
            'similitud': round(similarity, 3),
            'confianza_original': conf_orig,
            'confianza_ajustada': conf_new,
        })
        
        # Si la descripción de referencia es mejor, usarla
        desc_ref = best_elem.get('descripcion', '')
        desc_current = analysis.get('descripcion', '')
        if len(desc_ref) > len(desc_current):
            analysis['descripcion'] = desc_ref
        
        # Si el match es muy fuerte, confirmar que es de Huánuco
        if similarity > 0.75:
            analysis['es_de_huanuco'] = True
        
        # Mejorar contexto cultural si está disponible
        if 'contexto_cultural' in best_elem and len(best_elem['contexto_cultural']) > len(analysis.get('contexto_cultural', '')):
            analysis['contexto_cultural'] = best_elem['contexto_cultural']
    
    return analysis