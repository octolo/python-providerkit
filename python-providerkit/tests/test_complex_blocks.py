"""Behavior locks for the complex provider blocks, before any split."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from providerkit.commands.provider import _provider_command
from providerkit.helpers.load import autodiscover_providers, load_providers_from_json
from providerkit.kit import ProviderBase
from providerkit.providers.base import ProviderListBase


class _DemoProvider(ProviderBase):
    name = "demo"
    display_name = "Demo"

    def normalize(self, data, config):
        return {
            "value": data["value"],
            "service": self.current_service_name,
            "field_names": sorted(config.get("fields", {})),
        }


def _provider() -> _DemoProvider:
    return _DemoProvider(name="demo", display_name="Demo")


def test_get_nested_value_resolves_dicts_lists_and_fallbacks() -> None:
    provider = _provider()
    data = {"user": {"names": ["ada", "grace"], "city": None}}

    assert provider._get_nested_value(data, "user.names.1") == "grace"
    assert provider._get_nested_value(data, "user.names.9", "missing") == "missing"
    assert provider._get_nested_value(data, "user.names.nope", "missing") == "missing"
    assert provider._get_nested_value(data, "user.city", "missing") == "missing"
    assert provider._get_nested_value(data, "", "missing") == "missing"
    assert (
        provider._get_nested_value(data, ["missing.path", "user.names.0"], "missing")
        == "ada"
    )
    assert provider._get_nested_value(data, ["missing.path"], "missing") == "missing"
    assert provider._get_nested_value({"n": 0}, "n", "missing") == 0


def test_normalize_recursive_resolves_each_source_kind() -> None:
    provider = _provider()

    class Node:
        def __init__(self) -> None:
            self.child = {"label": "nested"}

        def read(self) -> str:
            return "called"

    node = Node()
    payload = {"item": node, "plain": "value"}

    assert provider._normalize_recursive(payload, "field", None) is None
    assert (
        provider._normalize_recursive(payload, "field", ["missing", "plain"]) == "value"
    )
    assert (
        provider._normalize_recursive(payload, "field", lambda data: data["plain"])
        == "value"
    )
    assert provider._normalize_recursive(payload, "field", "item.child.label") == (
        "nested"
    )
    assert provider._normalize_recursive(node, "field", "read") == "called"
    assert provider._normalize_recursive(payload, "field", "plain") == "value"
    assert provider._normalize_recursive(payload, "field", 7) == 7
    indexed = {"rows": [{"label": "first"}, {"label": "second"}]}
    assert provider._normalize_recursive(indexed, "field", "rows.1.label") == "second"
    assert provider._normalize_recursive(indexed, "field", "rows.9.label") is None
    assert provider._normalize_recursive(indexed, "field", "rows.nope") is None


def test_get_service_normalize_reports_cache_and_error_results() -> None:
    provider = _provider()
    del provider._service_results_cache

    with pytest.raises(ValueError, match="No cache found"):
        provider.get_service_normalize("lookup")

    provider._service_results_cache = {}
    with pytest.raises(ValueError, match="not found in cache"):
        provider.get_service_normalize("lookup")

    provider._service_results_cache = {"lookup": {}}
    with pytest.raises(ValueError, match="No result cached"):
        provider.get_service_normalize("lookup")

    provider._service_results_cache = {
        "lookup": {"result": {"error": "boom", "value": 1}}
    }
    assert provider.get_service_normalize("lookup") == {"error": "boom"}

    provider._service_results_cache = {
        "lookup": {"result": [{"error": "first"}, {"error": "second"}]}
    }
    assert provider.get_service_normalize("lookup") == {"error": "first"}


def test_get_service_normalize_uses_the_requested_service_config() -> None:
    provider = _provider()
    provider.services_cfg = {"lookup": {"fields": {"stored": {}}}}
    provider._service_results_cache = {"lookup": {"result": {"value": "ada"}}}

    assert provider.get_service_normalize("lookup") == {
        "value": "ada",
        "service": "lookup",
        "field_names": ["stored"],
    }
    assert provider.current_service_name is None

    overridden = provider.get_service_normalize(
        "lookup",
        services_cfg={"fields": {"override": {}}},
    )
    assert overridden["field_names"] == ["override"]


def test_get_service_normalize_normalizes_a_list_without_an_error() -> None:
    provider = _provider()
    provider.services_cfg = {"lookup": {"fields": {}}}
    provider._service_results_cache = {
        "lookup": {"result": [{"value": "ada"}, {"value": "grace"}]}
    }

    assert provider.get_service_normalize("lookup") == [
        {"value": "ada", "service": "lookup", "field_names": []},
        {"value": "grace", "service": "lookup", "field_names": []},
    ]
    assert provider.current_service_name is None


def test_provider_command_routes_flags_without_running_providers(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_execute(command, first, raw, output_format, additional_args) -> None:
        captured.update(
            {
                "command": command,
                "first": first,
                "raw": raw,
                "output_format": output_format,
                "additional_args": additional_args,
            }
        )

    monkeypatch.setattr(
        "providerkit.commands.provider._execute_command",
        fake_execute,
    )

    assert (
        _provider_command(
            [
                "--format",
                "json",
                "--dir",
                "/tmp/providers",
                "--json",
                "providers.json",
                "--filter",
                "spain",
                "--backend",
                "nominatim",
                "--first",
                "--raw",
                "--attr",
                "name=spain",
            ]
        )
        is True
    )
    assert captured == {
        "command": "get_providers",
        "first": True,
        "raw": True,
        "output_format": "json",
        "additional_args": {
            "dir_path": "/tmp/providers",
            "json": "providers.json",
            "query": "spain",
            "attribute_search": {"name": "spain"},
        },
    }


def test_provider_command_uses_backend_when_filter_is_absent(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_execute(command, first, raw, output_format, additional_args) -> None:
        captured["additional_args"] = additional_args

    monkeypatch.setattr(
        "providerkit.commands.provider._execute_command",
        fake_execute,
    )

    assert _provider_command(["--backend", "nominatim"]) is True
    assert captured["additional_args"] == {"query": "nominatim"}


def test_provider_command_rejects_positional_attributes(capsys) -> None:
    assert _provider_command(["--attr", "bad"]) is False
    assert "positional arguments not allowed" in capsys.readouterr().err


def test_provider_command_reads_a_command_payload(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_execute(command, first, raw, output_format, additional_args) -> None:
        captured["command"] = command
        captured["output_format"] = output_format
        captured["additional_args"] = additional_args

    monkeypatch.setattr(
        "providerkit.commands.provider._execute_command",
        fake_execute,
    )
    monkeypatch.setattr(
        "providerkit.commands.provider._parse_all_args",
        lambda _args: {
            "format": "xml",
            "command": {
                "args": ["get_alphabet", "latin", "verbose"],
                "kwargs": {"limit": "2"},
            },
        },
    )

    assert _provider_command(["ignored"]) is True
    assert captured == {
        "command": "get_alphabet",
        "output_format": "xml",
        "additional_args": {"query": "latin", "verbose": True, "limit": "2"},
    }


def test_provider_command_stops_when_parsing_returns_nothing(monkeypatch) -> None:
    monkeypatch.setattr(
        "providerkit.commands.provider._parse_all_args",
        lambda _args: {},
    )

    assert _provider_command(["ignored"]) is False


def test_loader_edges_before_splitting_discovery(tmp_path: Path) -> None:
    broken = tmp_path / "broken.json"
    broken.write_text("{", encoding="utf-8")

    assert load_providers_from_json({"providers": []}) == {}
    assert load_providers_from_json(json_path=broken) == {}
    assert autodiscover_providers(tmp_path / "missing") == {}


def test_autodiscover_infers_the_package_when_base_module_is_omitted() -> None:
    before = list(sys.path)

    found = autodiscover_providers("tests/test_providers_alphabet")

    assert set(found) == {
        "china_alphabet",
        "japan_alphabet",
        "france_alphabet",
        "spain_alphabet",
        "arabic_alphabet",
        "swahili_alphabet",
    }
    sys.path[:] = before


def test_autodiscover_loads_loose_files_and_skips_import_errors(
    tmp_path: Path,
) -> None:
    (tmp_path / "sample.py").write_text(
        "from providerkit.kit import ProviderBase\n"
        "class SampleProvider(ProviderBase):\n"
        "    name = 'sample'\n"
        "    display_name = 'Sample'\n",
        encoding="utf-8",
    )
    (tmp_path / "_hidden.py").write_text(
        "raise ImportError('hidden')\n",
        encoding="utf-8",
    )
    (tmp_path / "broken.py").write_text(
        "raise ImportError('broken')\n",
        encoding="utf-8",
    )

    found = autodiscover_providers(tmp_path)

    assert set(found) == {"sample"}
    assert found["sample"].__name__ == "SampleProvider"
    assert autodiscover_providers(tmp_path / "sample.py") == {}


def test_autodiscover_skips_modules_that_fail_inspection(tmp_path: Path) -> None:
    (tmp_path / "broken.py").write_text(
        "def __dir__():\n    raise ValueError('metadata unavailable')\n",
        encoding="utf-8",
    )
    (tmp_path / "valid.py").write_text(
        "from providerkit.kit import ProviderBase\n"
        "class ValidProvider(ProviderBase):\n"
        "    name = 'valid'\n",
        encoding="utf-8",
    )

    found = autodiscover_providers(tmp_path, base_module="")

    assert set(found) == {"valid"}


def test_provider_list_queries_delegate_to_get_providers() -> None:
    class _Listing(ProviderListBase):
        name = "listing"
        display_name = "Listing"

        def get_providers(self, *args, **kwargs):
            return [(args, kwargs)]

    listing = _Listing()
    forwarded = [(("latin",), {"limit": 2})]
    assert listing.get_config("latin", limit=2) == forwarded
    assert listing.get_package("latin", limit=2) == forwarded
    assert listing.get_service("latin", limit=2) == forwarded
    assert listing.get_urls("latin", limit=2) == forwarded
