import pytest

from app.clients.openrouter_client import (
    OpenRouterClient,
    OpenRouterError,
)


def test_openrouter_client_requires_api_key(monkeypatch):
    monkeypatch.setattr(
        "app.clients.openrouter_client.settings.openrouter_api_key",
        "",
    )

    with pytest.raises(
        OpenRouterError,
        match="OPENROUTER_API_KEY is not configured",
    ):
        OpenRouterClient()


def test_openrouter_client_parses_json_response(
    monkeypatch,
):
    monkeypatch.setattr(
        "app.clients.openrouter_client.settings.openrouter_api_key",
        "test-key",
    )

    class FakeResponse:
        status_code = 200

        def json(self):
            return {
                "choices": [
                    {
                        "message": {
                            "content": (
                                '{"result": "success"}'
                            )
                        }
                    }
                ]
            }

        text = ""

    def fake_post(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(
        "app.clients.openrouter_client.httpx.post",
        fake_post,
    )

    client = OpenRouterClient()

    result = client.generate_json(
        system_prompt="System",
        user_prompt="User",
    )

    assert result == {
        "result": "success",
    }


def test_openrouter_client_rejects_http_error(
    monkeypatch,
):
    monkeypatch.setattr(
        "app.clients.openrouter_client.settings.openrouter_api_key",
        "test-key",
    )

    class FakeResponse:
        status_code = 401
        text = "Unauthorized"

        def json(self):
            return {
                "error": {
                    "message": "Invalid API key",
                }
            }

    def fake_post(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(
        "app.clients.openrouter_client.httpx.post",
        fake_post,
    )

    client = OpenRouterClient()

    with pytest.raises(
        OpenRouterError,
        match="HTTP 401",
    ):
        client.generate_json(
            system_prompt="System",
            user_prompt="User",
        )


def test_openrouter_client_rejects_invalid_json(
    monkeypatch,
):
    monkeypatch.setattr(
        "app.clients.openrouter_client.settings.openrouter_api_key",
        "test-key",
    )

    class FakeResponse:
        status_code = 200

        def json(self):
            return {
                "choices": [
                    {
                        "message": {
                            "content": "not valid json",
                        }
                    }
                ]
            }

        text = ""

    def fake_post(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(
        "app.clients.openrouter_client.httpx.post",
        fake_post,
    )

    client = OpenRouterClient()

    with pytest.raises(
        OpenRouterError,
        match="invalid JSON",
    ):
        client.generate_json(
            system_prompt="System",
            user_prompt="User",
        )