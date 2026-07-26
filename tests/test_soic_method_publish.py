import yaml

from soic_method.models import Citation, LessonRecord, Rule, Span
from soic_method.publish import write_bundle
from soic_method.reconcile import ReconcileOutput


def _rule(tier, value=18):
    return Rule(tier=tier, kind="threshold", stage="screen", operator="lte",
                value=value, rule_key="screen.roc.floor", status="active",
                citations=[Citation(lesson_id="1", lesson_url="u",
                                    timestamp="00:41:12",
                                    span=Span(start=0, end=60), text_hash="h")])


def _lessons():
    return {"1": LessonRecord(lesson_id="1", course_title="c", module_title="m",
                              title="t", url="u", body_text="b", text_hash="h")}


def test_tiers_are_written_to_separate_files(tmp_path):
    out = ReconcileOutput(rules=[_rule("knockout"), _rule("graded", 15)])
    write_bundle(out, _lessons(), tmp_path)
    knock = yaml.safe_load((tmp_path / "knockouts.yaml").read_text())
    graded = yaml.safe_load((tmp_path / "graded.yaml").read_text())
    assert len(knock) == 1 and len(graded) == 1


def test_snapshot_records_corpus_hashes(tmp_path):
    write_bundle(ReconcileOutput(rules=[_rule("graded")]), _lessons(), tmp_path)
    snap = yaml.safe_load((tmp_path / "SNAPSHOT").read_text())
    assert snap["1"] == "h"


def test_conflicts_are_written_for_review(tmp_path):
    out = ReconcileOutput(conflicts=[[_rule("graded", 18), _rule("graded", 15)]])
    write_bundle(out, _lessons(), tmp_path)
    conflicts = yaml.safe_load((tmp_path / "conflicts.open.yaml").read_text())
    assert len(conflicts) == 1
    assert len(conflicts[0]) == 2


def test_gaps_lists_unbound_rules(tmp_path):
    write_bundle(ReconcileOutput(rules=[_rule("graded")]), _lessons(), tmp_path)
    assert "screen.roc.floor" in (tmp_path / "gaps.md").read_text()


def test_bundle_never_emits_a_bound_binding(tmp_path):
    write_bundle(ReconcileOutput(rules=[_rule("graded")]), _lessons(), tmp_path)
    text = (tmp_path / "graded.yaml").read_text()
    assert "bound" in text            # the word appears as "unbound"
    assert "status: bound" not in text


# --- Only `active` rules reach the executable files -------------------------
# final-branch-review.md I2. Partitioning was on `tier` alone, so a
# needs_audio_check knockout -- a rule the pipeline itself flagged for human
# ear verification -- shipped in knockouts.yaml indistinguishably from a
# corroborated one, and a consumer executing that file as hard exclusions
# would have applied it.

def test_non_active_knockout_does_not_ship_as_a_hard_exclusion(tmp_path):
    r = _rule("knockout").model_copy(update={"status": "needs_audio_check",
                                             "corroboration": 0})
    write_bundle(ReconcileOutput(rules=[r]), _lessons(), tmp_path)
    assert yaml.safe_load((tmp_path / "knockouts.yaml").read_text()) == []
    drafts = yaml.safe_load((tmp_path / "drafts.yaml").read_text())
    assert len(drafts) == 1
    assert drafts[0]["status"] == "needs_audio_check"


def test_non_active_graded_rule_is_routed_to_drafts(tmp_path):
    active = _rule("graded", 18)
    held = _rule("graded", 15).model_copy(update={"status": "needs_audio_check"})
    write_bundle(ReconcileOutput(rules=[active, held]), _lessons(), tmp_path)
    graded = yaml.safe_load((tmp_path / "graded.yaml").read_text())
    drafts = yaml.safe_load((tmp_path / "drafts.yaml").read_text())
    assert [g["value"] for g in graded] == [18]
    assert [d["value"] for d in drafts] == [15]


def test_pre_existing_drafts_are_preserved_alongside_withheld_rules(tmp_path):
    draft = _rule("graded", 12).model_copy(update={"status": "draft",
                                                   "rule_key": None})
    held = _rule("graded", 15).model_copy(update={"status": "needs_audio_check"})
    write_bundle(ReconcileOutput(rules=[held], drafts=[draft]),
                 _lessons(), tmp_path)
    drafts = yaml.safe_load((tmp_path / "drafts.yaml").read_text())
    assert sorted(d["value"] for d in drafts) == [12, 15]
