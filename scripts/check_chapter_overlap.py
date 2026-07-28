"""Flag sentences reused verbatim across chapters in generate_sdcourse_luc.py.

Chapter 6 originally reused Chapter 3's exact sentences because both cite the
same sdcourse.md source range (a "different angle, same citation" pairing the
plan intentionally repeats 14 more times across chapters 7-23). That bug was
caught only by the live multi-agent verification loop, one fix-and-reverify
cycle after the fact. This script gives a fast, offline first pass: it strips
HTML tags from each CH{n} block, splits into sentences, and reports any
sentence of a meaningful length that appears verbatim in more than one
chapter — the exact signature of a copy-pasted (rather than freshly
re-synthesized) passage.

Run after writing or editing any chapter:
    python3 scripts/check_chapter_overlap.py

A hit does not always mean a bug — a short verbatim quote from a persona file
legitimately appears in two chapters when both chapters cite that persona's
same source line range (e.g. a Bloom Filters "Key Insight" quote). Use
judgment: a shared PROSE sentence (the chapter's own synthesis, not a quoted
line) is the pattern worth fixing.
"""
import re
import sys

MIN_SENTENCE_CHARS = 60  # ignore short/boilerplate matches


def load_chapters(path):
    src = open(path).read()
    chapters = {}
    for m in re.finditer(r'^CH(\d+) = """(.*?)\n"""', src, re.S | re.M):
        n = int(m.group(1))
        html = m.group(2)
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text).strip()
        chapters[n] = text
    return chapters


def sentences(text):
    # Rough sentence split; good enough for a similarity-scan heuristic.
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip()) >= MIN_SENTENCE_CHARS]


def main(path='scripts/generate_sdcourse_luc.py'):
    chapters = load_chapters(path)
    by_sentence = {}
    for n, text in chapters.items():
        for s in sentences(text):
            by_sentence.setdefault(s, set()).add(n)

    hits = {s: chs for s, chs in by_sentence.items() if len(chs) > 1}
    if not hits:
        print(f"No verbatim sentence overlap found across {len(chapters)} chapters.")
        return 0

    print(f"Found {len(hits)} sentence(s) shared verbatim across chapters:\n")
    for s, chs in sorted(hits.items(), key=lambda kv: sorted(kv[1])):
        chapter_list = ', '.join(f'Ch{c}' for c in sorted(chs))
        print(f"[{chapter_list}]")
        print(f"  {s[:200]}{'...' if len(s) > 200 else ''}\n")
    return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else 'scripts/generate_sdcourse_luc.py'))
