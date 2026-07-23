import json
from pathlib import Path
from unittest.mock import MagicMock, patch

REGISTRY_FIXTURE = Path(__file__).parent / "fixtures" / "notebooks_sample.yaml"


def test_load_notebook_registry_parses_company_to_notebook_id():
    from soic_senses.notebook_client import load_notebook_registry

    registry = load_notebook_registry(REGISTRY_FIXTURE)

    assert registry["IGL"] == "ec56de21-0518-415b-a2d8-c09920fe594e"
    assert registry["ABB"] == "46bb9f4e-800d-4fed-9dbf-546c5a563500"


def test_resolve_notebook_id_returns_id_for_known_company():
    from soic_senses.notebook_client import load_notebook_registry, resolve_notebook_id

    registry = load_notebook_registry(REGISTRY_FIXTURE)

    assert resolve_notebook_id("IGL", registry) == "ec56de21-0518-415b-a2d8-c09920fe594e"


def test_resolve_notebook_id_is_case_insensitive():
    from soic_senses.notebook_client import load_notebook_registry, resolve_notebook_id

    registry = load_notebook_registry(REGISTRY_FIXTURE)

    assert resolve_notebook_id("igl", registry) == "ec56de21-0518-415b-a2d8-c09920fe594e"


def test_resolve_notebook_id_raises_for_unregistered_company():
    from soic_senses.notebook_client import (
        NotebookUnavailableError,
        load_notebook_registry,
        resolve_notebook_id,
    )

    registry = load_notebook_registry(REGISTRY_FIXTURE)

    try:
        resolve_notebook_id("VENUSPIPES", registry)
        assert False, "expected NotebookUnavailableError"
    except NotebookUnavailableError as exc:
        assert "VENUSPIPES" in str(exc)


def test_ask_notebook_raises_auth_error_when_no_cached_tokens():
    from soic_senses.notebook_client import NotebookAuthError, ask_notebook

    with patch("soic_senses.notebook_client._load_cached_tokens", return_value=None):
        try:
            ask_notebook("some-id", "What is the margin trend?")
            assert False, "expected NotebookAuthError"
        except NotebookAuthError as exc:
            assert "auth.json" in str(exc)


def test_ask_notebook_returns_answer_on_success():
    from soic_senses.notebook_client import ask_notebook

    fake_client = MagicMock()
    fake_client.query.return_value = {
        "answer": "Margins expanded 200bps YoY.",
        "conversation_id": "conv-1",
        "turn_number": 1,
    }

    with patch("soic_senses.notebook_client._load_cached_tokens", return_value=object()), patch(
        "soic_senses.notebook_client._build_client", return_value=fake_client
    ):
        result = ask_notebook("some-id", "What is the margin trend?")

    assert result["answer"] == "Margins expanded 200bps YoY."
    assert result["conversation_id"] == "conv-1"


def test_ask_notebook_wraps_client_exception_as_query_error():
    from soic_senses.notebook_client import NotebookQueryError, ask_notebook

    fake_client = MagicMock()
    fake_client.query.side_effect = RuntimeError("Authentication expired")

    with patch("soic_senses.notebook_client._load_cached_tokens", return_value=object()), patch(
        "soic_senses.notebook_client._build_client", return_value=fake_client
    ):
        try:
            ask_notebook("some-id", "What is the margin trend?")
            assert False, "expected NotebookQueryError"
        except NotebookQueryError as exc:
            assert "Authentication expired" in str(exc)


def test_append_receipt_assigns_stable_incrementing_tags(tmp_path):
    from soic_senses.notebook_client import append_receipt

    log_path = tmp_path / "query_log.jsonl"

    tag1 = append_receipt(
        log_path, company="IGL", question="Q1?", result={"answer": "A1", "conversation_id": "c1"}
    )
    tag2 = append_receipt(
        log_path, company="IGL", question="Q2?", result={"answer": "A2", "conversation_id": "c1"}
    )
    tag3 = append_receipt(
        log_path, company="ABB", question="Q1?", result={"answer": "A3", "conversation_id": "c2"}
    )

    assert tag1 == "[Q1]"
    assert tag2 == "[Q2]"
    assert tag3 == "[Q1]"  # separate company, own counter

    lines = log_path.read_text().splitlines()
    assert len(lines) == 3
    first = json.loads(lines[0])
    assert first["company"] == "IGL"
    assert first["tag"] == "[Q1]"
    assert first["answer"] == "A1"


def test_query_company_raises_without_calling_ask_notebook_when_unregistered():
    from soic_senses.notebook_client import NotebookUnavailableError, query_company

    with patch("soic_senses.notebook_client.ask_notebook") as mock_ask:
        try:
            query_company(
                company="VENUSPIPES",
                question="Any red flags?",
                registry_path=REGISTRY_FIXTURE,
                log_path=None,
            )
            assert False, "expected NotebookUnavailableError"
        except NotebookUnavailableError:
            pass

    mock_ask.assert_not_called()


def test_query_company_tags_and_logs_receipt(tmp_path):
    from soic_senses.notebook_client import query_company

    log_path = tmp_path / "query_log.jsonl"
    fake_result = {"answer": "Margins expanded.", "conversation_id": "conv-1", "turn_number": 1}

    with patch("soic_senses.notebook_client.ask_notebook", return_value=fake_result) as mock_ask:
        receipt = query_company(
            company="IGL",
            question="What is the margin trend?",
            registry_path=REGISTRY_FIXTURE,
            log_path=log_path,
        )

    mock_ask.assert_called_once_with(
        "ec56de21-0518-415b-a2d8-c09920fe594e", "What is the margin trend?", conversation_id=None
    )
    assert receipt["tag"] == "[Q1]"
    assert receipt["answer"] == "Margins expanded."
    assert log_path.exists()
