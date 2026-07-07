import json
import subprocess
import sys
from pathlib import Path

REPO = Path("/Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper"
            "/.claude/worktrees/bold-sammet-8c78b3")
PY = "/Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.venv/bin/python"


def _run(args, **kw):
    env = {"PYTHONPATH": "src", "PATH": "/usr/bin:/bin"}
    return subprocess.run([PY, "-m", "storm_core", *args], cwd=REPO, env=env,
                          capture_output=True, text=True, **kw)


def test_roster_subcommand_emits_json(tmp_path, monkeypatch):
    (tmp_path / "a.md").write_text("---\nname: al\ndescription: d\n---\n", encoding="utf-8")
    env = {"PYTHONPATH": "src", "PATH": "/usr/bin:/bin", "STORM_ROSTER_DIR": str(tmp_path)}
    out = subprocess.run([PY, "-m", "storm_core", "roster"], cwd=REPO, env=env,
                         capture_output=True, text=True)
    data = json.loads(out.stdout)
    assert data == [{"name": "al", "slug": "a", "description": "d"}]


def test_build_writes_note_and_html(tmp_path):
    report = {
        "topic": "Zakat Advisory", "mode": "idea", "summary": "s", "verdict": "KEEP",
        "lenses": ["Operator"], "findings": [], "contradictions": [],
        "halal_note": "", "generated": "2026-07-06",
    }
    rj = tmp_path / "r.json"
    rj.write_text(json.dumps(report), encoding="utf-8")
    reports = tmp_path / "reports"
    html = tmp_path / "html"
    out = _run(["build", "--report", str(rj), "--reports-dir", str(reports),
                "--html-dir", str(html)])
    assert out.returncode == 0, out.stderr
    assert (reports / "zakat-advisory.md").exists()
    assert (html / "zakat-advisory.html").exists()
    assert "zakat-advisory.md" in out.stdout


def test_build_bad_report_exits_1_with_message(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text('{"not":"a storm report"}', encoding="utf-8")
    out = _run(["build", "--report", str(bad), "--reports-dir", str(tmp_path),
                "--html-dir", str(tmp_path)])
    assert out.returncode == 1
    assert "error:" in out.stderr
