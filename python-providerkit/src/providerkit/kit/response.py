import csv
import json
import re
import xml.etree.ElementTree as ET
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from collections.abc import Callable

from clicommands.utils import format_tabulate

# XML 1.0 Name, without namespace colons or supplementary characters in tags.
_XML_NAME_START = (
    "A-Z_a-z"
    "\u00c0-\u00d6\u00d8-\u00f6\u00f8-\u02ff"
    "\u0370-\u037d\u037f-\u1fff"
    "\u200c-\u200d\u2070-\u218f"
    "\u2c00-\u2fef\u3001-\ud7ff"
    "\uf900-\ufdcf\ufdf0-\ufffd"
)
_XML_NAME_CHAR = _XML_NAME_START + "\\-.0-9\u00b7\u0300-\u036f\u203f-\u2040"
_INVALID_XML_NAME_CHAR = re.compile(f"[^{_XML_NAME_CHAR}]")
_XML_NAME_START_CHAR = re.compile(f"[{_XML_NAME_START}]")
_NON_ASCII_CHAR = re.compile(r"[^\x00-\x7f]")
_INVALID_XML_CHAR = re.compile("[^\t\n\r\x20-\ud7ff\ue000-\ufffd\U00010000-\U0010ffff]")


def _sanitize_xml_name(name: str) -> str:
    """Return an XML element name ElementTree can serialize and parse."""
    cleaned = name.strip()
    if not cleaned:
        return "item"
    cleaned = _INVALID_XML_NAME_CHAR.sub("_", cleaned)
    if _XML_NAME_START_CHAR.match(cleaned) is None:
        cleaned = f"_{cleaned}"
    if cleaned.lower().startswith("xml"):
        cleaned = f"_{cleaned}"
    if not cleaned.isascii():
        # Expat can reject some names allowed by the XML specification.
        # Only the name already filtered above is used in this probe.
        try:
            ET.fromstring(f"<{cleaned}/>")
        except ET.ParseError:
            cleaned = _NON_ASCII_CHAR.sub("_", cleaned)
    return cleaned


class ResponseMixin:
    """Mixin for handling responses."""

    def response(
        self, service_name: str, raw: bool = False, output_format: str | None = None
    ) -> str:
        if raw:
            get_result: Callable[[str], Any] = cast(
                "Callable[[str], Any]",
                getattr(self, "get_service_result", lambda _: ""),
            )
            result = get_result(service_name)
            return str(result)
        if output_format and hasattr(self, f"response_{output_format}"):
            return str(getattr(self, f"response_{output_format}")(service_name))
        get_normalize: Callable[[str], Any] = cast(
            "Callable[[str], Any]", getattr(self, "get_service_normalize", lambda _: "")
        )
        normalize = get_normalize(service_name)
        return str(normalize)

    def response_terminal(self, service_name: str) -> str:
        """Response in terminal."""
        get_normalize: Callable[..., Any] = cast(
            "Callable[..., Any]",
            getattr(self, "get_service_normalize", lambda *_args, **_kwargs: {}),
        )
        response: Any = get_normalize(service_name, raw=False)
        return str(format_tabulate(response, empty_message="No data available."))

    def response_json(self, service_name: str) -> str:
        get_normalize: Callable[[str], Any] = cast(
            "Callable[[str], Any]", getattr(self, "get_service_normalize", lambda _: {})
        )
        response: Any = get_normalize(service_name)
        return json.dumps(response, indent=2, ensure_ascii=False)

    def response_xml(self, service_name: str) -> str:
        """Render XML, replacing forbidden characters with U+FFFD."""
        get_normalize: Callable[[str], Any] = cast(
            "Callable[[str], Any]", getattr(self, "get_service_normalize", lambda _: {})
        )
        response: Any = get_normalize(service_name)

        def dict_to_xml(data: Any, parent: ET.Element) -> None:
            if isinstance(data, dict):
                for key, value in data.items():
                    original_name = str(key)
                    xml_name = _sanitize_xml_name(original_name)
                    elem = ET.SubElement(parent, xml_name)
                    if xml_name != original_name:
                        safe_name = _INVALID_XML_CHAR.sub("\ufffd", original_name)
                        elem.set("original_name", safe_name)
                    dict_to_xml(value, elem)
            elif isinstance(data, list):
                for item in data:
                    elem = ET.SubElement(parent, "item")
                    dict_to_xml(item, elem)
            else:
                text = "" if data is None else str(data)
                parent.text = _INVALID_XML_CHAR.sub("\ufffd", text)

        root = ET.Element("response")
        dict_to_xml(response, root)
        ET.indent(root)
        return ET.tostring(root, encoding="unicode")

    def response_csv(self, service_name: str) -> str:
        """Convert response to CSV format."""
        import io

        get_normalize: Callable[[str], Any] = cast(
            "Callable[[str], Any]", getattr(self, "get_service_normalize", lambda _: {})
        )
        response: Any = get_normalize(service_name)
        output = io.StringIO()
        writer = csv.writer(output)

        if isinstance(response, list):
            if not response:
                return ""
            if isinstance(response[0], dict):
                headers = list(response[0].keys())
                writer.writerow(headers)
                for item in response:
                    writer.writerow([item.get(k, "") for k in headers])
            else:
                writer.writerow(response)
        elif isinstance(response, dict):
            for key, value in sorted(response.items()):
                writer.writerow([key, value])
        else:
            writer.writerow([str(response)])

        return output.getvalue()
