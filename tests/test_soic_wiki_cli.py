import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import yaml
from typer.testing import CliRunner

runner = CliRunner()

FRAMEWORKS_FIXTURE = Path(__file__).parent / "fixtures" / "frameworks_sample.md"
SECTOR_REGISTRY_FIXTURE = Path(__file__).parent / "fixtures" / "sector_notebooks_sample.yaml"


def test_briefing_command_prints_markdown():
    from soic_wiki.cli import app

    fake_briefing = MagicMock()
    fake_briefing.to_markdown.return_value = "# Decision Briefing — TCS\n\nsome content"

    with patch("soic_wiki.cli.build_briefing", return_value=fake_briefing) as mock_build:
        result = runner.invoke(
            app,
            [
                "briefing",
                "TCS",
                "--keyword", "dcf",
                "--keyword", "intrinsic value",
                "--frameworks", str(FRAMEWORKS_FIXTURE),
            ],
        )

    assert result.exit_code == 0
    assert "Decision Briefing — TCS" in result.stdout
    mock_build.assert_called_once_with(
        symbol="TCS",
        keywords=["dcf", "intrinsic value"],
        frameworks_path=str(FRAMEWORKS_FIXTURE),
        sector_registry_path=None,
    )


def test_briefing_command_passes_sector_registry_when_given():
    from soic_wiki.cli import app

    fake_briefing = MagicMock()
    fake_briefing.to_markdown.return_value = "content"

    with patch("soic_wiki.cli.build_briefing", return_value=fake_briefing) as mock_build:
        runner.invoke(
            app,
            [
                "briefing",
                "TCS",
                "--keyword", "dcf",
                "--frameworks", str(FRAMEWORKS_FIXTURE),
                "--sectors", str(SECTOR_REGISTRY_FIXTURE),
            ],
        )

    mock_build.assert_called_once_with(
        symbol="TCS",
        keywords=["dcf"],
        frameworks_path=str(FRAMEWORKS_FIXTURE),
        sector_registry_path=str(SECTOR_REGISTRY_FIXTURE),
    )


def test_run_sector_command_writes_notes_and_refs_and_reports_gate_verdict(tmp_path, monkeypatch):
    from soic_wiki.cli import app
    from soic_wiki.notebooklm_sector_pipeline import ConceptProposal, SectorRunResult

    monkeypatch.chdir(tmp_path)
    registry_path = tmp_path / "sector_notebooks.yaml"
    registry_path.write_text(yaml.safe_dump({"notebooks": {}}))

    fake_lessons = [
        MagicMock(lesson_id="111", module_title="Fluorine Industry", title="Part 1", body_text="raw text")
    ]
    fake_result = SectorRunResult(
        slug="fluorine-industry",
        notebook_id="nb-1",
        ref_codes={"111": "FLUOR"},
        concepts=[ConceptProposal(title="Concept One", scope="s", sources=["FLUOR"], timestamps="x")],
        notes={"concept-one": "## The mechanism\n\nBody."},
    )

    from soic_wiki.sector_gate import AcceptanceReport

    fake_report = AcceptanceReport(verdict=True, g2_verified=19, g2_total=20)

    with patch("soic_wiki.cli.load_corpus", return_value=fake_lessons), patch(
        "soic_wiki.cli.run_sector_pipeline", return_value=fake_result
    ) as mock_run, patch(
        "soic_wiki.cli.run_sector_acceptance_report", return_value=fake_report
    ) as mock_gate:
        result = runner.invoke(
            app,
            [
                "run-sector",
                "Fluorine Industry",
                "--slug", "fluorine-industry",
                "--corpus", "data/content.json",
                "--sector-registry", str(registry_path),
                "--out-dir", str(tmp_path / "out"),
            ],
        )

    assert result.exit_code == 0
    mock_run.assert_called_once()
    mock_gate.assert_called_once()

    notes_dir = tmp_path / "out" / "notes"
    assert (notes_dir / "concept-one.md").read_text() == "## The mechanism\n\nBody."

    refs = json.loads((tmp_path / "out" / "refs.json").read_text())
    assert refs == {"111": "FLUOR"}

    assert "PASS" in result.stdout


def test_run_sector_command_excludes_ineligible_lessons_before_seeding(tmp_path, monkeypatch):
    """A lesson excluded via configs/course_eligibility.yaml's
    excluded_lessons (e.g. a real guest handoff mid-lesson) must never be
    seeded to NotebookLM as a source -- the 2026-07-27 "SOIC Market
    Signals" incident showed the CLI feeding an excluded lesson's content
    to NotebookLM anyway, only caught after the fact when a note happened
    to cite it (the sector_gate G3 check). This test locks in the fix:
    filtering must happen before run_sector_pipeline is ever called."""
    from soic_method.models import LessonRecord
    from soic_wiki.cli import app
    from soic_wiki.notebooklm_sector_pipeline import SectorRunResult

    monkeypatch.chdir(tmp_path)

    eligibility_path = tmp_path / "configs" / "course_eligibility.yaml"
    eligibility_path.parent.mkdir(parents=True)
    eligibility_path.write_text(
        yaml.safe_dump(
            {
                "courses": {"Market Signals Course": {"eligible": True, "transcript_fidelity": "verbatim"}},
                "excluded_lessons": ["Guest Segment Lesson"],
            }
        )
    )

    registry_path = tmp_path / "sector_notebooks.yaml"
    registry_path.write_text(yaml.safe_dump({"notebooks": {}}))

    fake_lessons = [
        LessonRecord(
            lesson_id="111",
            course_title="Market Signals Course",
            module_title="Market Signals",
            title="Eligible Lesson",
            url="u1",
            body_text="raw text",
        ),
        LessonRecord(
            lesson_id="222",
            course_title="Market Signals Course",
            module_title="Market Signals",
            title="Guest Segment Lesson",
            url="u2",
            body_text="guest text",
        ),
    ]
    fake_result = SectorRunResult(
        slug="market-signals", notebook_id="nb-1", ref_codes={"111": "MARKA"}, concepts=[], notes={}
    )

    from soic_wiki.sector_gate import AcceptanceReport

    fake_report = AcceptanceReport(verdict=True, g2_verified=0, g2_total=0)

    with patch("soic_wiki.cli.load_corpus", return_value=fake_lessons), patch(
        "soic_wiki.cli.run_sector_pipeline", return_value=fake_result
    ) as mock_run, patch("soic_wiki.cli.run_sector_acceptance_report", return_value=fake_report):
        runner.invoke(
            app,
            [
                "run-sector",
                "Market Signals",
                "--slug", "market-signals",
                "--corpus", "data/content.json",
                "--sector-registry", str(registry_path),
                "--out-dir", str(tmp_path / "out"),
                "--course-eligibility", str(eligibility_path),
            ],
        )

    mock_run.assert_called_once()
    passed_lessons = mock_run.call_args.kwargs["lessons"]
    passed_ids = {l["lesson_id"] for l in passed_lessons}
    assert passed_ids == {"111"}  # "222" (the excluded guest lesson) never reaches the pipeline


def test_run_sector_command_fails_loudly_when_module_title_not_found(tmp_path, monkeypatch):
    from soic_wiki.cli import app

    monkeypatch.chdir(tmp_path)

    with patch("soic_wiki.cli.load_corpus", return_value=[]):
        result = runner.invoke(
            app, ["run-sector", "Nonexistent Module", "--slug", "x", "--out-dir", str(tmp_path / "out")]
        )

    assert result.exit_code != 0
    assert "Nonexistent Module" in result.stdout


def test_evolve_frameworks_command_writes_a_preview_file_never_the_real_frameworks_file(tmp_path, monkeypatch):
    from soic_wiki.cli import app

    monkeypatch.chdir(tmp_path)
    frameworks_copy = tmp_path / "frameworks.md"
    frameworks_copy.write_text(FRAMEWORKS_FIXTURE.read_text())
    original = frameworks_copy.read_text()

    fake_answer = (
        "### REINFORCES F1\nSome grounding addition.\n"
    )

    with patch("soic_wiki.cli.ask_notebook", return_value={"answer": fake_answer, "conversation_id": "c1"}):
        result = runner.invoke(
            app,
            [
                "evolve-frameworks",
                "--notebook-id", "nb-1",
                "--sector-title", "Fluorine Industry",
                "--frameworks", str(frameworks_copy),
                "--out", str(tmp_path / "diff.md"),
            ],
        )

    assert result.exit_code == 0
    assert frameworks_copy.read_text() == original  # never touched
    diff_text = (tmp_path / "diff.md").read_text()
    assert "NOT YET APPLIED" in diff_text
    assert "F1" in diff_text
