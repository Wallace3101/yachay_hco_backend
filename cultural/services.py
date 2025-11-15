import json, hashlib, logging
from typing import Dict, Optional
from django.conf import settings
from django.core.cache import cache

from .analysis.constants import PROMPT_VERSION, MIN_CONFIDENCE_THRESHOLD
from .analysis.prompt import build_analysis_prompt
from .analysis.parsing import parse_response
from .analysis.validation import validate_with_local_knowledge
from .analysis.openai_client import call_openai_api, OpenAIClientError

logger = logging.getLogger(__name__)

class OpenAIAnalysisError(Exception): pass

class CulturalAnalysisService:
    API_URL = "https://api.openai.com/v1/chat/completions"
    MODEL = getattr(settings, 'OPENAI_MODEL', 'gpt-4o')
    MAX_TOKENS = getattr(settings, 'OPENAI_MAX_TOKENS', 1000)
    # ! tiempo para llamadas a OpenAI(Aunmentar según necesidad)
    TIMEOUT = getattr(settings, 'OPENAI_TIMEOUT', 60)
    MIN_CONFIDENCE_THRESHOLD = getattr(settings, 'MIN_CONFIDENCE_THRESHOLD', MIN_CONFIDENCE_THRESHOLD)

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        if not self.api_key or self.api_key == 'your_api_key_here':
            raise ValueError("OPENAI_API_KEY no está configurada")

    def analyze_image(self, image_base64: str, use_cache: bool = True) -> Dict:
        try:
            # caché
            if use_cache:
                cached = self._get_cached_analysis(image_base64)
                if cached:
                    logger.info("Análisis desde caché")
                    return cached

            prompt = build_analysis_prompt()
            raw = call_openai_api(
                api_url=self.API_URL,
                api_key=self.api_key,
                model=self.MODEL,
                max_tokens=self.MAX_TOKENS,
                timeout=self.TIMEOUT,
                prompt=prompt,
                image_base64=image_base64,
            )

            analysis = parse_response(raw)
            analysis = validate_with_local_knowledge(analysis)

            if analysis.get('confianza', 0.0) < self.MIN_CONFIDENCE_THRESHOLD:
                raise OpenAIAnalysisError(
                    f"Confianza insuficiente ({analysis['confianza']:.2f}). " +
                    analysis.get('descripcion', 'No se pudo identificar como elemento cultural de Huánuco')
                )

            analysis['metadata'] = {
                'model': self.MODEL,
                'prompt_version': PROMPT_VERSION,
                'tokens_used': raw.get('usage', {}).get('total_tokens', 0),
                'cached': False
            }

            if use_cache:
                self._cache_analysis(image_base64, analysis)

            logger.info(f"Análisis OK: {analysis['titulo']} (confianza: {analysis['confianza']:.2f})")
            return analysis

        except OpenAIClientError as e:
            logger.error(f"Error OpenAI: {e}")
            raise OpenAIAnalysisError(str(e))
        except Exception as e:
            logger.error(f"Error inesperado: {e}", exc_info=True)
            raise OpenAIAnalysisError(f"Error al procesar la imagen: {str(e)}")

    # === caché (igual que ya tenías) ===
    def _get_cached_analysis(self, image_base64: str) -> Optional[Dict]:
        try:
            h = hashlib.md5(image_base64.encode()).hexdigest()
            key = f'cultural_analysis:{h}'
            cached = cache.get(key)
            if cached:
                cached['metadata']['cached'] = True
            return cached
        except Exception as e:
            logger.warning(f"Error obteniendo caché: {str(e)}")
            return None

    def _cache_analysis(self, image_base64: str, analysis: Dict) -> None:
        try:
            h = hashlib.md5(image_base64.encode()).hexdigest()
            key = f'cultural_analysis:{h}'
            cache.set(key, analysis, timeout=86400)
        except Exception as e:
            logger.warning(f"Error guardando en caché: {str(e)}")

# Helper público (no cambia)
def analyze_cultural_image(image_base64: str, use_cache: bool = True) -> Dict:
    service = CulturalAnalysisService()
    return service.analyze_image(image_base64, use_cache=use_cache)
