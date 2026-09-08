from pathlib import Path
import re
from typing import Any


class KnowledgeStore:
    def __init__(self, root: Path) -> None:
        self._root = root.resolve()

    def search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        terms = self._tokenize(query)

        results: list[dict[str, Any]] = []

        for path in self._root.rglob("*.md"):
            text = path.read_text(
                encoding="utf-8"
            )

            lower_text = text.lower()

            relative_path = path.relative_to(
                self._root
            ).as_posix()

            lower_path = relative_path.lower()

            score = 0

            for term in terms:
                score += lower_text.count(term)

                if term in lower_path:
                    score += 5

            if score == 0:
                continue

            snippet = self._create_snippet(
                text=text,
                terms=terms,
            )

            results.append(
                {
                    "path": relative_path,
                    "score": score,
                    "snippet": snippet,
                }
            )

        results.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return results[:limit]

    def read_document(
        self,
        relative_path: str,
    ) -> dict[str, Any]:
        path = (
            self._root / relative_path
        ).resolve()

        try:
            path.relative_to(self._root)
        except ValueError:
            raise ValueError(
                "Document path is outside "
                "the allowed documentation directory."
            )

        if path.suffix.lower() != ".md":
            raise ValueError(
                "Only Markdown documents are allowed."
            )

        if not path.is_file():
            raise FileNotFoundError(
                f"Document not found: {relative_path}"
            )

        text = path.read_text(
            encoding="utf-8"
        )

        max_chars = 12_000

        return {
            "path": relative_path,
            "content": text[:max_chars],
            "truncated": len(text) > max_chars,
        }

    @staticmethod
    def _tokenize(
        query: str,
    ) -> list[str]:
        return [
            token.lower()
            for token in re.findall(
                r"[a-zA-Z0-9_.-]{3,}",
                query,
            )
        ]

    @staticmethod
    def _create_snippet(
        text: str,
        terms: list[str],
    ) -> str:
        lower = text.lower()

        positions = [
            lower.find(term)
            for term in terms
            if lower.find(term) >= 0
        ]

        position = min(positions) if positions else 0

        start = max(
            0,
            position - 250,
        )

        end = min(
            len(text),
            position + 750,
        )

        return text[start:end]