from app.core.agent_cache import InMemoryMD5Cache


def test_cache_returns_stored_value() -> None:
    cache = InMemoryMD5Cache[str]()

    cache.set(
        question="What is the highest customer value?",
        schema_context="customers(id, lifetime_value)",
        value="customers",
    )

    result = cache.get(
        question="What is the highest customer value?",
        schema_context="customers(id, lifetime_value)",
    )

    assert result == "customers"


def test_cache_misses_for_different_question() -> None:
    cache = InMemoryMD5Cache[str]()

    cache.set(
        question="What is the highest customer value?",
        schema_context="customers(id, lifetime_value)",
        value="customers",
    )

    result = cache.get(
        question="Which country has the highest customer value?",
        schema_context="customers(id, lifetime_value)",
    )

    assert result is None


def test_cache_misses_for_different_schema() -> None:
    cache = InMemoryMD5Cache[str]()

    cache.set(
        question="What is the highest customer value?",
        schema_context="customers(id, lifetime_value)",
        value="customers",
    )

    result = cache.get(
        question="What is the highest customer value?",
        schema_context="customers(id, lifetime_value, country)",
    )

    assert result is None


def test_cache_key_is_deterministic() -> None:
    cache = InMemoryMD5Cache[str]()

    key_one = cache.build_key(
        question="What is the highest customer value?",
        schema_context="customers(id, lifetime_value)",
    )

    key_two = cache.build_key(
        question="What is the highest customer value?",
        schema_context="customers(id, lifetime_value)",
    )

    assert key_one == key_two
    assert len(key_one) == 32


def test_cache_clear() -> None:
    cache = InMemoryMD5Cache[str]()

    cache.set(
        question="Question",
        schema_context="Schema",
        value="result",
    )

    assert cache.size() == 1

    cache.clear()

    assert cache.size() == 0