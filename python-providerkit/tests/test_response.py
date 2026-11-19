"""Regression tests for terminal and XML response rendering."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from providerkit.kit.response import ResponseMixin


class _Catalog(ResponseMixin):
    def __init__(self, payload: dict[str, str]) -> None:
        self.payload = payload
        self.kwargs: dict[str, object] | None = None

    def get_service_normalize(
        self, service_name: str, **kwargs: object
    ) -> dict[str, str]:
        self.kwargs = {"service_name": service_name, **kwargs}
        return self.payload


def _parsed_xml(payload: dict[str, str]) -> ET.Element:
    document = _Catalog(payload).response_xml("demo")
    return ET.fromstring(document)


def _child(root: ET.Element, tag: str) -> ET.Element:
    for element in root:
        if element.tag == tag:
            return element
    raise AssertionError(tag)


def test_response_terminal_fallback_accepts_raw_flag() -> None:
    rendered = ResponseMixin().response_terminal("demo")

    assert rendered == "No data available."


def test_response_terminal_forwards_raw_flag_to_normalize() -> None:
    catalog = _Catalog({"service": "demo", "value": "1"})

    rendered = catalog.response_terminal("demo")

    assert catalog.kwargs == {"service_name": "demo", "raw": False}
    assert "service" in rendered
    assert "demo" in rendered
    assert "value" in rendered


def test_response_xml_repairs_empty_and_invalid_starts() -> None:
    root = _parsed_xml(
        {
            "": "empty",
            "-label": "minus",
            ".hidden": "dot",
            "+plus": "plus",
            "1name": "digit",
        }
    )

    assert _child(root, "item").text == "empty"
    assert _child(root, "item").get("original_name") == ""
    assert _child(root, "_-label").text == "minus"
    assert _child(root, "_-label").get("original_name") == "-label"
    assert _child(root, "_.hidden").text == "dot"
    assert _child(root, "_plus").text == "plus"
    assert _child(root, "_1name").text == "digit"


def test_response_xml_avoids_prefixes_and_reserved_names() -> None:
    root = _parsed_xml(
        {
            "foo:bar": "prefixed",
            "xml": "reserved",
            "XMLConfig": "reserved-prefix",
        }
    )

    assert _child(root, "foo_bar").text == "prefixed"
    assert _child(root, "foo_bar").get("original_name") == "foo:bar"
    assert _child(root, "_xml").text == "reserved"
    assert _child(root, "_XMLConfig").text == "reserved-prefix"
    for element in root.iter():
        assert ":" not in element.tag
        assert not element.tag.lower().startswith("xml")


def test_response_xml_preserves_unicode_names() -> None:
    root = _parsed_xml({"été": "ete", "名前": "tokyo"})

    assert _child(root, "été").text == "ete"
    assert _child(root, "été").get("original_name") is None
    assert _child(root, "名前").text == "tokyo"


def test_response_xml_keeps_emoji_in_original_name() -> None:
    root = _parsed_xml({"😀": "demo"})

    element = _child(root, "_")
    assert element.text == "demo"
    assert element.get("original_name") == "😀"


def test_response_xml_replaces_forbidden_characters() -> None:
    root = _parsed_xml({"a\x00b": "first\x01\ud800\t\nsecond"})

    element = _child(root, "a_b")
    assert element.get("original_name") == "a\ufffdb"
    assert element.text == "first\ufffd\ufffd\t\nsecond"


def test_response_xml_can_be_reparsed_with_a_unicode_joiner() -> None:
    key = "\u200cname"
    (element,) = _parsed_xml({key: "demo"})

    assert element.text == "demo"
    assert element.get("original_name", element.tag) == key
