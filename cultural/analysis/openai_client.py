import requests
from requests.exceptions import Timeout

class OpenAIClientError(Exception):
    pass

def call_openai_api(
    api_url: str,
    api_key: str,
    model: str,
    max_tokens: int,
    timeout: int,
    prompt: str,
    image_base64: str
  ) -> dict:
    """
    Envía la imagen + prompt a OpenAI y retorna el JSON de respuesta.
    Incluye un mensaje de sistema para forzar formato JSON puro.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # 💡 Añadimos un mensaje de "system" para controlar el formato
    messages = [
        {
            "role": "system",
            "content": (
                "Eres un analista cultural experto en Huánuco, Perú. "
                "Responde únicamente con un JSON válido y bien formado, sin texto adicional, sin markdown, "
                "sin explicaciones ni comentarios fuera del JSON."
            ),
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                },
            ],
        },
    ]

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
    }

    try:
        r = requests.post(api_url, headers=headers, json=payload, timeout=timeout)
        r.raise_for_status()
        return r.json()

    except Timeout:
        raise OpenAIClientError("Timeout en llamada a OpenAI")
    except requests.HTTPError as e:
        if e.response is not None:
            if e.response.status_code == 429:
                raise OpenAIClientError("Límite de uso de la API excedido")
            if e.response.status_code == 401:
                raise OpenAIClientError("Error de autenticación con OpenAI")
            raise OpenAIClientError(
                f"Error en la API: {e.response.status_code} - {e.response.text}"
            )
        raise OpenAIClientError("HTTPError sin respuesta")
