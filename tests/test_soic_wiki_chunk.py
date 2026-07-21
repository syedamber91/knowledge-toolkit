from soic_wiki.chunk import MarkerIndex, chunk_transcript

BODY = (
    "[00:00:05] alpha alpha alpha\n"
    "[00:01:10] beta beta beta\n"
    "[00:02:20] gamma gamma gamma\n"
)


def test_timestamp_at_picks_nearest_preceding_marker():
    idx = MarkerIndex(BODY)
    assert idx.timestamp_at(BODY.index("beta")) == "00:01:10"
    assert idx.timestamp_at(BODY.index("gamma")) == "00:02:20"


def test_timestamp_before_any_marker_is_zero():
    assert MarkerIndex("no markers").timestamp_at(3) == "00:00:00"


def _marker_spans(text):
    from soic_wiki.chunk import MARKER
    return [(m.start(), m.end()) for m in MARKER.finditer(text)]


def test_marker_index_matches_the_linear_scan_at_all_content_positions():
    # The index replaces soic_method.corpus.resolve_timestamp for speed
    # (measured ~1170x on the largest real lesson). At every position that
    # points at actual transcript CONTENT -- which is the only kind of
    # position a citation span ever uses -- the two must agree exactly.
    from soic_method.corpus import resolve_timestamp
    idx = MarkerIndex(BODY)
    inside = {p for s, e in _marker_spans(BODY) for p in range(s, e)}
    for pos in range(len(BODY)):
        if pos in inside:
            continue
        assert idx.timestamp_at(pos) == resolve_timestamp(BODY, pos)


def test_index_diverges_deliberately_inside_a_marker():
    """A documented, intentional behaviour change.

    `resolve_timestamp` bounds its scan with `finditer(text, 0, start+1)`, so
    the ENTIRE 10-char marker must fit before start+1. Ask it for a position
    inside a marker's own bracket text and it reports the marker BEFORE that
    one (or 00:00:00). Task 5's round-3 review flagged this as a latent edge
    case and judged it untriggerable in practice, since spans start at
    content.

    The index answers "the marker you are inside of", which is the correct
    reading. Pinned here so the divergence is a recorded decision rather than
    an accident discovered later.
    """
    from soic_method.corpus import resolve_timestamp
    idx = MarkerIndex(BODY)
    inside_first = 5           # inside "[00:00:05]", which spans 0..9
    assert idx.timestamp_at(inside_first) == "00:00:05"
    assert resolve_timestamp(BODY, inside_first) == "00:00:00"


def test_next_marker_at_or_after():
    idx = MarkerIndex(BODY)
    assert idx.next_marker_at_or_after(0) == 0
    assert idx.next_marker_at_or_after(1) == BODY.index("[00:01:10]")
    assert idx.next_marker_at_or_after(len(BODY)) is None


def _long_body(n_markers=60, filler=400):
    parts = []
    for i in range(n_markers):
        parts.append("[%02d:%02d:%02d] " % (i // 3600, (i // 60) % 60, i % 60))
        parts.append("x" * filler)
    return "".join(parts)


def test_chunks_cover_the_whole_transcript_without_gaps():
    body = _long_body()
    chunks = chunk_transcript("L1", body)
    assert chunks[0].start == 0
    assert chunks[-1].end == len(body)
    for a, b in zip(chunks, chunks[1:]):
        # Overlapping is fine; a GAP would silently lose transcript.
        assert b.start <= a.end


def test_every_chunk_boundary_lands_on_a_marker():
    body = _long_body()
    idx = MarkerIndex(body)
    starts = set(idx.offsets)
    chunks = chunk_transcript("L1", body)
    # Every start except the first should be a marker offset.
    for c in chunks[1:]:
        assert c.start in starts


def test_chunks_carry_resolvable_timestamps():
    chunks = chunk_transcript("L1", _long_body())
    for c in chunks:
        assert c.ts_start != "" and c.ts_end != ""
        assert c.text == _long_body()[c.start:c.end]


def test_empty_transcript_yields_no_chunks():
    assert chunk_transcript("L1", "") == []


def test_marker_free_text_still_chunks_without_running_away():
    # No markers to snap to: cuts must still happen, not grow unbounded.
    body = "y" * 20000
    chunks = chunk_transcript("L1", body)
    assert len(chunks) > 1
    assert chunks[-1].end == len(body)
    assert all(c.ts_start == "00:00:00" for c in chunks)
