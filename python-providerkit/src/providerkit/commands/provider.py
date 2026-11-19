"""Provider command for listing and filtering providers."""

from __future__ import annotations

import sys
from typing import Any, cast

from clicommands.helpers import _get_package_name_from_path, _CLI_CONTEXT
from clicommands.commands import parse_args_from_config
from clicommands.commands.base import Command
from clicommands.utils import print_header, print_separator

from providerkit.helpers import get_providerkit

# Parser arguments configuration
_PROVIDER_COMMAND_CONFIG = {
    "format": {"type": str, "default": "terminal"},
    "first": {"type": "store_true"},
    "raw": {"type": "store_true"},
    "filter": {"type": str},
    "backend": {"type": str},
    "attr": {"type": str, "nargs": "*", "default": []},
}

_ARG_CONFIG = {
    **_PROVIDER_COMMAND_CONFIG,
    "command": {"type": str, "nargs": "*", "default": []},
    "dir": {"type": str},
    "json": {"type": str},
}


def _parse_all_args(args: list[str]) -> dict[str, Any]:
    result = parse_args_from_config(args, _ARG_CONFIG, prog="provider")
    return cast("dict[str, Any]", result)


def _execute_command(
    command: str,
    first: bool,
    raw: bool,
    output_format: str,
    additional_args: dict[str, str | bool],
) -> None:
    """Execute the provider command."""
    cli_path = _CLI_CONTEXT.get("cli_file_path")
    package_name = _get_package_name_from_path(cli_path) if cli_path else "unknown"
    pvk = get_providerkit(**additional_args)

    if command in [
        "get_providers",
        "get_config",
        "get_package",
        "get_service",
        "get_urls",
    ]:
        pvk.call_service(command, lib_name=package_name, **additional_args)
        print(pvk.response(command, raw, output_format=output_format))
    else:
        pvk.execute_providers(command, first, **additional_args)

        for pv in pvk.get_service_result(command):
            provider = pv["provider"]
            print_separator()
            print_header(provider.name)
            print_separator()
            print(provider.response(command, raw, output_format=output_format))
            print()


def _command_from_payload(cmd_data: Any) -> tuple[str, dict[str, Any]]:
    command = "get_providers"
    additional_args: dict[str, Any] = {}
    if not isinstance(cmd_data, dict) or "args" not in cmd_data:
        return command, additional_args

    args = cmd_data["args"]
    if args:
        command = args[0]
        if len(args) > 1:
            additional_args["query"] = args[1]
        for arg in args[2:]:
            additional_args[arg] = True
    additional_args.update(cmd_data.get("kwargs", {}))
    return command, additional_args


def _string_option(parsed: dict[str, Any], key: str) -> str | None:
    value = parsed.get(key, None)
    if key not in parsed or not isinstance(value, str):
        return None
    return value


def _attribute_search(attr_data: dict[str, Any]) -> dict[str, str] | None:
    if attr_data.get("args"):
        print(
            "Invalid attribute format: positional arguments not allowed. Expected format: key=value",
            file=sys.stderr,
        )
        return None
    kwargs_data = attr_data.get("kwargs", {})
    if isinstance(kwargs_data, dict):
        return cast("dict[str, str]", kwargs_data)
    return {}


def _provider_command(args: list[str]) -> bool:
    """Execute provider command with parsed arguments."""
    parsed = _parse_all_args(args)
    if not parsed:
        return False

    command, additional_args = _command_from_payload(parsed.get("command"))
    dir_path = _string_option(parsed, "dir")
    if dir_path is not None:
        additional_args["dir_path"] = dir_path
    json_path = _string_option(parsed, "json")
    if json_path is not None:
        additional_args["json"] = json_path

    query = _string_option(parsed, "filter")
    if query is None and "filter" not in parsed:
        query = _string_option(parsed, "backend")
    if query is not None:
        additional_args["query"] = query

    if "attr" in parsed and isinstance(parsed["attr"], dict):
        attribute_search = _attribute_search(parsed["attr"])
        if attribute_search is None:
            return False
        additional_args["attribute_search"] = attribute_search

    _execute_command(
        command,
        parsed.get("first", False),
        parsed.get("raw", False),
        parsed.get("format", "terminal"),
        additional_args,
    )
    return True


provider_command = Command(
    _provider_command,
    "List and filter providers (use --list [query] --format [terminal|json|xml])",
)
