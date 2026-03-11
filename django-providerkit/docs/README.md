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

### Django ProviderKit-Specific Guidelines

- **Model development**: Provider models must inherit from `ProviderModel` or `ServiceModel`
- **Virtual models**: All models use `managed = False` and inherit from `VirtualModel`
- **ProviderKit integration**: Use ProviderKit's field definitions and metadata
- **Field mapping**: Map ProviderKit field types to Django model fields via `fields_associations`
- **Admin integration**: Provide Django admin interface for viewing and managing providers

### Model Implementation Checklist

When creating a new provider model:
- [ ] Inherit from `ProviderModel` or `ServiceModel`
- [ ] Set `managed = False` in Meta
- [ ] Use ProviderKit's field definitions
- [ ] Map fields using `fields_associations`
- [ ] Configure Django admin if needed
- [ ] Add tests for the model

