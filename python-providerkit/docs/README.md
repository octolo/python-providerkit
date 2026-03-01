## Assistant Guidelines

This file provides general guidelines for the AI assistant working on this project.

For detailed information, refer to:
- `AI.md` - Condensed reference guide for AI assistants (start here)
- `purpose.md` - Project purpose and goals
- `structure.md` - Project structure and module organization
- `development.md` - Development guidelines and best practices

### Quick Reference

- Always use `./service.py dev <command>` or `python dev.py <command>` for project tooling
- Always use `./service.py quality <command>` or `python quality.py <command>` for quality checks
- Maintain clean module organization and separation of concerns
- Default to English for all code artifacts (comments, docstrings, logging, error strings, documentation snippets, etc.)
- Follow Python best practices and quality standards
- Keep dependencies minimal and prefer standard library
- Ensure all public APIs have type hints and docstrings
- Write tests for new functionality

### ProviderKit-Specific Guidelines

- **Provider creation**: Providers must inherit from `ProviderBase`
- **Mixin architecture**: Use PackageMixin, ConfigMixin, ServiceMixin, UrlsMixin as needed
- **Discovery**: Use `autodiscover_providers()`, `get_providers()`, or `load_providers_from_json()`
- **Imports**: Always use standard imports from `providerkit`; never manipulate `sys.path`
