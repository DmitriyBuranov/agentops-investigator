from pathlib import Path

import pytest

from agentops_investigator.knowledge.store import KnowledgeStore


def test_search_finds_matching_document(
    tmp_path: Path,
) -> None:
    runbooks = tmp_path / "runbooks"
    runbooks.mkdir()

    document = runbooks / "payment-errors.md"

    document.write_text(
        "Payment HTTP 500 errors after deployment.",
        encoding="utf-8",
    )

    store = KnowledgeStore(tmp_path)

    results = store.search(
        "payment deployment"
    )

    assert len(results) == 1
    assert (
        results[0]["path"]
        == "runbooks/payment-errors.md"
    )


def test_cannot_read_outside_docs(
    tmp_path: Path,
) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()

    secret = tmp_path / "secret.txt"

    secret.write_text(
        "secret",
        encoding="utf-8",
    )

    store = KnowledgeStore(docs)

    with pytest.raises(ValueError):
        store.read_document(
            "../secret.txt"
        )