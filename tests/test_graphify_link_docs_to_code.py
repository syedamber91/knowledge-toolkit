"""graphify keeps docs and code as two islands (2 of 9,611 edges crossed in the 2026-10-03 graph). The linker adds
doc -> code edges where a doc node literally names a code file or function, and only when the name is unambiguous."""

import importlib.util
import pathlib

_PATH = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "graphify_link_docs_to_code.py"


def _load():
    spec = importlib.util.spec_from_file_location("graphify_link_docs_to_code", _PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def code(i, label, src):
    return {"id": i, "label": label, "file_type": "code", "source_file": src}


def doc(i, label, src="CLAUDE.md", ft="document"):
    return {"id": i, "label": label, "file_type": ft, "source_file": src}


def graph(nodes, links=()):
    return {"nodes": list(nodes), "links": list(links)}


SECTOR_GATE = code("c_sg", "sector_gate.py", "src/soic_wiki/sector_gate.py")


def test_a_doc_naming_a_file_by_path_gets_an_extracted_edge():
    m = _load()
    new = m.link_docs_to_code(graph([doc("d1", "soic_wiki/sector_gate.py gates"), SECTOR_GATE]))
    assert len(new) == 1
    e = new[0]
    assert (e["source"], e["target"], e["relation"], e["confidence"]) == ("d1", "c_sg", "references", "EXTRACTED")
    assert e["source_file"] == "CLAUDE.md"


def test_a_bare_file_name_that_is_unique_gets_an_inferred_edge():
    m = _load()
    new = m.link_docs_to_code(graph([doc("d1", "the gate lives in sector_gate.py"), SECTOR_GATE]))
    assert [(e["target"], e["confidence"]) for e in new] == [("c_sg", "INFERRED")]


def test_an_ambiguous_bare_file_name_is_not_linked():
    m = _load()
    nodes = [doc("d1", "defined in models.py"), code("a", "models.py", "src/a/models.py"), code("b", "models.py", "src/b/models.py")]
    assert m.link_docs_to_code(graph(nodes)) == []


def test_a_path_disambiguates_a_file_name_that_exists_twice():
    m = _load()
    nodes = [doc("d1", "see soic_method/models.py"), code("a", "models.py", "src/soic_wiki/models.py"),
             code("b", "models.py", "src/soic_method/models.py")]
    assert [e["target"] for e in m.link_docs_to_code(graph(nodes))] == ["b"]


def test_a_unique_function_call_in_a_doc_label_is_linked():
    m = _load()
    nodes = [doc("d1", "calls verify_rule() before publishing"), code("f", "verify_rule()", "src/soic_method/verify.py")]
    assert [(e["target"], e["confidence"]) for e in m.link_docs_to_code(graph(nodes))] == [("f", "INFERRED")]


def test_a_function_name_defined_twice_is_not_linked():
    m = _load()
    nodes = [doc("d1", "entry point is main()"), code("a", "main()", "src/a/cli.py"), code("b", "main()", "src/b/cli.py")]
    assert m.link_docs_to_code(graph(nodes)) == []


def test_a_generic_one_word_call_is_not_linked_even_when_it_is_unique():
    m = _load()
    nodes = [doc("d1", "normalize() exact slug-set matching rule"), code("f", "normalize()", "scripts/learn_by_doing.py")]
    assert m.link_docs_to_code(graph(nodes)) == []


def test_a_unique_snake_case_identifier_is_linked_to_its_function():
    m = _load()
    nodes = [doc("d1", "both gates normalize with normalize_slice first"), code("f", "normalize_slice()", "src/soic_method/corpus.py")]
    assert [e["target"] for e in m.link_docs_to_code(graph(nodes))] == ["f"]


def test_a_node_never_links_to_code_in_its_own_file():
    m = _load()
    nodes = [doc("r1", "Docstring about sector_gate.py itself", src="src/soic_wiki/sector_gate.py", ft="rationale"), SECTOR_GATE]
    assert m.link_docs_to_code(graph(nodes)) == []


def test_only_doc_nodes_are_sources_and_only_code_nodes_are_targets():
    m = _load()
    nodes = [code("c1", "uses sector_gate.py", "src/x.py"), doc("d1", "about sector_gate.py"), doc("d2", "also sector_gate.py")]
    nodes.append(SECTOR_GATE)
    assert sorted(e["source"] for e in m.link_docs_to_code(graph(nodes))) == ["d1", "d2"]


def test_existing_links_are_not_duplicated_and_apply_is_idempotent():
    m = _load()
    data = graph([doc("d1", "soic_wiki/sector_gate.py gates"), SECTOR_GATE])
    assert m.apply_links(data) == 1
    assert m.apply_links(data) == 0
    assert len(data["links"]) == 1
    existing = graph([doc("d1", "soic_wiki/sector_gate.py gates"), SECTOR_GATE],
                     [{"source": "c_sg", "target": "d1", "relation": "x", "confidence": "EXTRACTED"}])
    assert m.link_docs_to_code(existing) == []  # an edge in either direction counts


def test_a_label_with_no_code_reference_gets_nothing():
    m = _load()
    assert m.link_docs_to_code(graph([doc("d1", "General discussion of valuation"), SECTOR_GATE])) == []
