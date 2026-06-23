import media_toolkit.store as store
import media_toolkit.web as web

# A realistic, clearly-extractable article (enough body for trafilatura).
_PARA = ("Caching with Redis and load balancing across microservices are core "
         "system design techniques. Kubernetes orchestrates the containers while "
         "Kafka handles the streaming events between services. ")
HTML = (
    "<html><head><title>System Design Basics</title>"
    "<meta name='author' content='Jane Doe'></head><body>"
    "<nav>home about</nav>"
    "<article><h1>System Design Basics</h1>"
    + "".join(f"<p>{_PARA}</p>" for _ in range(8))
    + "</article><footer>copyright</footer></body></html>"
)


def test_item_from_html_extracts_readable_article():
    item = web.item_from_html("https://blog.example.com/system-design", HTML)
    assert item is not None
    assert item.kind == "article"
    assert item.title == "System Design Basics"
    assert item.source_id == "blog.example.com"
    assert item.body_markdown  # boilerplate stripped, body kept
    assert "nav" not in item.body_markdown.lower()[:20]
    # topic matching across the extended vocabulary
    assert "System Design" in item.topics
    assert "Kubernetes" in item.topics or "Caching" in item.topics


def test_item_from_html_empty_returns_none():
    assert web.item_from_html("https://x.com/a", "") is None


def test_capture_urls_batch_and_resume(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "CONTENT_PATH", tmp_path / "media.json")
    monkeypatch.setattr(web.time, "sleep", lambda *a, **k: None)

    pages = {
        "https://blog.example.com/a": HTML.replace("System Design Basics", "Article A"),
        "https://blog.example.com/b": HTML.replace("System Design Basics", "Article B"),
    }
    cat = web.capture_urls(list(pages), html_fetch=lambda u: pages[u])
    assert {i.title for i in cat.items} == {"Article A", "Article B"}

    # resume: same URLs -> no duplicates
    cat2 = web.capture_urls(list(pages), html_fetch=lambda u: pages[u])
    assert len(cat2.items) == 2
