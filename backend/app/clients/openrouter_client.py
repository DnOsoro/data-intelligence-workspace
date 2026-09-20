import json

import httpx

from app.core.settings import settings


class OpenRouterError(RuntimeError):
    """Raised when an OpenRouter request fails."""


class OpenRouterClient:
    def __init__(self) -> None:
        if not settings.openrouter_api_key:
            raise OpenRouterError(
                "OPENROUTER_API_KEY is not configured."
            )

        self.api_key = settings.openrouter_api_key
        self.model = settings.openrouter_model
        self.base_url = settings.openrouter_base_url.rstrip("/")

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> dict:
        url = f"{self.base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        if settings.openrouter_http_referer:
            headers["HTTP-Referer"] = (
                settings.openrouter_http_referer
            )

        if settings.openrouter_x_title:
            headers["X-Title"] = settings.openrouter_x_title

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "max_tokens": settings.openrouter_max_tokens,
            "response_format": {
                "type": "json_object",
            },
        }

        try:
            response = httpx.post(
                url,
                headers=headers,
                json=payload,
                timeout=60.0,
            )
        except httpx.HTTPError as exc:
            raise OpenRouterError(
                f"OpenRouter request failed: {exc}"
            ) from exc

        if response.status_code >= 400:
            try:
                error_payload = response.json()
            except ValueError:
                error_payload = response.text

            raise OpenRouterError(
                f"OpenRouter returned HTTP "
                f"{response.status_code}: "
                f"{error_payload}"
            )

        try:
            response_payload = response.json()
            content = response_payload["choices"][0]["message"][
                "content"
            ]
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise OpenRouterError(
                "OpenRouter returned an unexpected response."
            ) from exc

        if not isinstance(content, str) or not content.strip():
            raise OpenRouterError(
                "OpenRouter returned an empty response."
            )

        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as exc:
            raise OpenRouterError(
                "OpenRouter returned invalid JSON."
            ) from exc

        if not isinstance(parsed, dict):
            raise OpenRouterError(
                "OpenRouter JSON response must be an object."
            )

        return parsed