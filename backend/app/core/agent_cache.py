import hashlib
from typing import Generic, TypeVar


T = TypeVar("T")


class InMemoryMD5Cache(Generic[T]):
    def __init__(self) -> None:
        self._cache: dict[str, T] = {}

    def build_key(
        self,
        question: str,
        schema_context: str,
    ) -> str:
        cache_input = (
            f"question:{question.strip()}\n"
            f"schema:{schema_context.strip()}"
        )

        return hashlib.md5(
            cache_input.encode("utf-8")
        ).hexdigest()

    def get(
        self,
        question: str,
        schema_context: str,
    ) -> T | None:
        key = self.build_key(
            question=question,
            schema_context=schema_context,
        )

        return self._cache.get(key)

    def set(
        self,
        question: str,
        schema_context: str,
        value: T,
    ) -> None:
        key = self.build_key(
            question=question,
            schema_context=schema_context,
        )

        self._cache[key] = value

    def clear(self) -> None:
        self._cache.clear()

    def size(self) -> int:
        return len(self._cache)