import media_core.store as store
import youtube_toolkit.capture as yt


def _info(vid, title, desc=""):
    return {
        "id": vid, "title": title,
        "webpage_url": f"https://www.youtube.com/watch?v={vid}",
        "channel": "DataChan", "channel_id": "UC1", "uploader": "DataChan",
        "upload_date": "20250101", "duration": 612, "description": desc,
    }


def test_video_id_of_handles_url_forms():
    VID = "dQw4w9WgXcQ"  # 11 chars
    assert yt.video_id_of(f"https://www.youtube.com/watch?v={VID}") == VID
    assert yt.video_id_of(f"https://youtu.be/{VID}") == VID
    assert yt.video_id_of(f"https://www.youtube.com/shorts/{VID}") == VID
    assert yt.video_id_of(VID) == VID  # bare 11-char id
    assert yt.video_id_of("https://www.youtube.com/@chan") == ""  # not a video


def test_capture_single_video(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "CONTENT_PATH", tmp_path / "media.json")
    monkeypatch.setattr(yt.time, "sleep", lambda *a, **k: None)

    cat = yt.capture(
        "https://www.youtube.com/watch?v=abcdefghijk",
        info_fetch=lambda u: _info("abcdefghijk", "Intro to Kafka", "apache kafka streaming"),
        transcript_fetch=lambda vid: "kafka is a distributed streaming platform",
        entries_fetch=lambda u: [],
    )
    assert len(cat.items) == 1
    it = cat.items[0]
    assert it.kind == "youtube"
    assert it.title == "Intro to Kafka"
    assert it.source == "DataChan"
    assert it.body_accessible is True
    assert "Apache Kafka" in it.topics and "Streaming" in it.topics
    assert it.published_at.year == 2025
    assert (tmp_path / "media.json").exists()


def test_capture_channel_respects_limit_and_resumes(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "CONTENT_PATH", tmp_path / "media.json")
    monkeypatch.setattr(yt.time, "sleep", lambda *a, **k: None)

    entries = [{"id": "vid00000001"}, {"id": "vid00000002"}, {"id": "vid00000003"}]
    infos = {e["id"]: _info(e["id"], f"Video {e['id']}") for e in entries}

    cat = yt.capture(
        "https://www.youtube.com/@DataChan",
        limit=2,
        info_fetch=lambda u: infos[yt.video_id_of(u)],
        transcript_fetch=lambda vid: "content",
        entries_fetch=lambda u: entries,
    )
    assert len(cat.items) == 2  # limit honored

    # second run with same data -> no duplicates
    cat2 = yt.capture(
        "https://www.youtube.com/@DataChan", limit=2,
        info_fetch=lambda u: infos[yt.video_id_of(u)],
        transcript_fetch=lambda vid: "content",
        entries_fetch=lambda u: entries,
    )
    assert len(cat2.items) == 2


def test_missing_transcript_marks_inaccessible(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "CONTENT_PATH", tmp_path / "media.json")
    monkeypatch.setattr(yt.time, "sleep", lambda *a, **k: None)

    cat = yt.capture(
        "https://www.youtube.com/watch?v=abcdefghijk",
        info_fetch=lambda u: _info("abcdefghijk", "No Captions Here"),
        transcript_fetch=lambda vid: "",   # transcripts disabled
        entries_fetch=lambda u: [],
    )
    it = cat.items[0]
    assert it.body_accessible is False
    assert it.body_markdown == ""
