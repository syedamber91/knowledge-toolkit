from soic_toolkit.mindmap import build_markdown
from soic_toolkit.models import Catalog, Course, Lesson, Module


def _catalog():
    return Catalog(
        base_url="https://learn.soic.in",
        courses=[
            Course(
                title="Valuation",
                url="https://learn.soic.in/learn/valuation",
                modules=[
                    Module(
                        title="Fundamentals",
                        lessons=[
                            Lesson(
                                title="Intrinsic Value",
                                url="https://learn.soic.in/learn/lesson-1",
                                key_points=["Worth based on fundamentals", "Use a margin of safety"],
                            )
                        ],
                    )
                ],
            )
        ],
    )


def test_markdown_hierarchy_and_links():
    md = build_markdown(_catalog(), title="My Map")
    assert "# My Map" in md
    assert "## Valuation" in md
    assert "### Fundamentals" in md
    assert "- [Intrinsic Value](https://learn.soic.in/learn/lesson-1)" in md
    assert "  - Worth based on fundamentals" in md


def test_frontmatter_present():
    md = build_markdown(_catalog())
    assert md.startswith("---\nmarkmap:")
