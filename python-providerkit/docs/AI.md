# AI Assistant Contract — ProviderKit

**This document is the single source of truth for all AI-generated work in this repository.**  
All instructions in this file **override default AI behavior**.

Any AI assistant working on this project **must strictly follow this document**.

If a request conflicts with this document, **this document always wins**.

---

## Rule Priority

Rules in this document have the following priority order:

1. **ABSOLUTE RULES** — must always be followed, no exception
2. **REQUIRED RULES** — mandatory unless explicitly stated otherwise
3. **REQUIRED PRACTICES** — should be followed unless there is a clear reason not to
4. **INFORMATIONAL SECTIONS** — context and reference only

---

## ABSOLUTE RULES

These rules must always be followed.

- Follow this `AI.md` file exactly
- Do not invent new services, commands, abstractions, patterns, or architectures
- Do not refactor, redesign, or optimize unless explicitly requested
- Do not manipulate `sys.path`
- Do not use filesystem-based imports to access `clicommands` or `providerkit`
- Do not hardcode secrets, credentials, tokens, or API keys
- Do not execute tooling commands outside the approved entry points
- **Comments**: Only add comments to resolve ambiguity or uncertainty. Do not comment obvious code.
- **Dependencies**: Add dependencies only when absolutely necessary. Prefer standard library always.
- If a request violates this document:
  - Stop
  - Explain the conflict briefly
  - Ask for clarification

---

## REQUIRED RULES

### Language and Communication

- **Language**: English only
  - Code
  - Comments
  - Docstrings
  - Logs
  - Error messages
  - Documentation
- Be concise, technical, and explicit
- Avoid unnecessary explanations unless requested

### Code Simplicity and Minimalism

- **Write the simplest possible code**: Always choose the simplest solution that works
- **Minimal dependencies**: Add dependencies only when absolutely necessary. Prefer standard library. Only add when essential functionality cannot be reasonably implemented otherwise
- **Minimal comments**: Comments only to resolve ambiguity or uncertainty. Do not comment obvious code or reiterate what the code already states clearly
- **Good factorization**: Factorize code when it improves clarity and reduces duplication, but only if it doesn't add unnecessary complexity or abstraction

---

## ProviderKit Overview (INFORMATIONAL)

**ProviderKit** is a generic provider management library for Python. It provides a standardized way to manage, discover, and interact with multiple service providers in a unified manner.

### Core Functionality

1. **Discover and enumerate providers** with essential metadata:
   - Provider name (human-readable)
   - Unique identifier (for programmatic access)
   - Dependency package availability
   - Configuration readiness
   - Documentation access
   - Status information
   - Website URL

2. **Implement business logic** through a modular mixin-based architecture:
   - `ProviderBase`: Core provider base class that combines all mixins
   - `PackageMixin`: Package dependency management and validation
   - `ServiceMixin`: Business logic implementation and service methods
   - `UrlsMixin`: URL routing and endpoint management (if applicable)
   - `ConfigMixin`: Configuration management and validation

### Use Cases

- Multi-provider integrations (email, SMS, payment, etc.)
- Provider fallback mechanisms
- Provider discovery and selection
- Configuration validation across multiple providers
- Unified interface for heterogeneous services

---

## Architecture (REQUIRED)

- Mixin-based architecture with domain-specific mixins
- `ProviderBase` class combines all mixins (PackageMixin, UrlsMixin, ConfigMixin, ServiceMixin)
- Provider discovery from JSON, configuration, or directory scanning
- Automatic validation of dependencies and configuration
- Consistent interface across provider implementations

---

## Project Structure (INFORMATIONAL)

```
python-providerkit/
├── src/providerkit/          # Main package
│   ├── kit/                  # Core provider infrastructure
│   ├── providers/            # Provider implementations
│   ├── commands/             # Command infrastructure
│   ├── helpers/              # Utility functions
│   └── cli.py                # CLI interface
├── tests/                    # Test suite
├── docs/                     # Documentation
└── pyproject.toml
```

---

## Command Execution (ABSOLUTE)

- **Always use**: `./service.py dev <command>` or `python dev.py <command>`
- **Always use**: `./service.py quality <command>` or `python quality.py <command>`
- Never execute commands directly without going through these entry points

---

## Code Standards (REQUIRED)

### Typing and Documentation

- All public functions and methods **must** have complete type hints
- Use **Google-style docstrings** for public classes, methods, and functions
- Document raised exceptions in docstrings where relevant

### Testing

- Use **pytest** exclusively
- All tests must live in the `tests/` directory
- New features and bug fixes require corresponding tests

### Linting and Formatting

- Follow **PEP 8**
- Use configured tools: `ruff`, `mypy`
- Use the configured formatter: `ruff format`

---

## Code Quality Principles (REQUIRED)

- **Simplicity first**: Write the simplest possible solution. Avoid complexity unless clearly necessary.
- **Minimal dependencies**: Minimize dependencies. Only add when essential functionality cannot be reasonably implemented otherwise. Always prefer standard library.
- **No over-engineering**: Do not add abstractions, patterns, or layers unless they solve a real problem.
- **Comments**: Minimal, only to resolve ambiguity or uncertainty.
- **Separation of concerns**: One responsibility per module
- **Good factorization**: Factorize when it improves clarity without adding complexity

---

## ProviderKit Integration (ABSOLUTE)

- `providerkit` is an installed package
- Always use standard Python imports:
  - `from providerkit import ProviderBase`
  - `from providerkit.kit import PackageMixin, ConfigMixin, ServiceMixin, UrlsMixin`
  - `from providerkit.helpers import get_providers, autodiscover_providers, try_providers`
- Never manipulate import paths
- Never use file-based or relative imports to access `providerkit`
- For dynamic imports, use `importlib.import_module()` from the standard library

---

## Clicommands Integration (ABSOLUTE)

- `clicommands` is an installed package (dependency of providerkit, used for CLI)
- Always use standard Python imports from `clicommands.commands` and `clicommands.utils`
- No path manipulation
- Direct imports only: `from clicommands.commands import ...` or `from clicommands.utils import ...`
- Use `importlib.import_module()` for dynamic imports

---

## Provider Architecture (REQUIRED)

### Creating Providers

Providers must inherit from `ProviderBase`:

```python
from providerkit import ProviderBase

class MyProvider(ProviderBase):
    name = "my_provider"
    display_name = "My Provider"
    description = "Description of my provider"

    def __init__(self, **kwargs):
        super().__init__(name="my_provider", display_name="My Provider", **kwargs)
```

### Provider Discovery

- Use `autodiscover_providers()` to discover providers from a directory
- Use `get_providers()` to load providers from JSON, config, or directory
- Use `load_providers_from_json()` for JSON-based loading

---

## Environment Variables (REQUIRED)

- `ENVFILE_PATH`: Path to `.env` file (relative to project root if not absolute)
- `ENSURE_VIRTUALENV`: Set to `1` to activate `.venv` if it exists
- Provider-specific: Use prefixes (e.g., `NOMINATIM_`, `GOOGLE_MAPS_`, etc.)

---

## Error Handling (REQUIRED)

- Handle errors gracefully
- Use appropriate exception types
- Provide clear, actionable error messages
- Do not swallow exceptions silently
- Document exceptions in docstrings
- Handle API rate limits and failures with retry logic when appropriate
- Support provider fallback mechanisms for resilience

---

## Configuration and Secrets (ABSOLUTE)

- Never hardcode: API keys, credentials, tokens, secrets
- Use environment variables or configuration files
- Use provider-specific configuration prefixes
- Clearly document required configuration

---

## Versioning (REQUIRED)

- Follow **Semantic Versioning (SemVer)**
- Update versions appropriately
- Clearly document breaking changes

---

## CLI System (INFORMATIONAL)

ProviderKit discovers commands from:
1. `commands/` directory
2. `.commands.json` configuration file

### Command Creation Rules

- Use `Command` class from `commands.base` or define functions ending with `_command`
- Commands must accept `args: list[str]` and return `bool`

---

## Anti-Hallucination Clause (ABSOLUTE)

If a requested change is not supported by this document, not aligned with the existing codebase, or requiring assumptions:

1. Stop
2. Explain what is unclear or conflicting
3. Ask for clarification

Do not guess. Do not invent.

---

## Quick Compliance Checklist

- [ ] All rules in `AI.md` are respected
- [ ] No forbidden behavior
- [ ] Code is simple, minimal, explicit
- [ ] Dependencies minimal (prefer standard library)
- [ ] Comments only resolve ambiguity
- [ ] Imports follow ProviderKit and Qualitybase rules
- [ ] Public APIs typed and documented
- [ ] Providers inherit from ProviderBase correctly
- [ ] No secrets or credentials exposed
- [ ] Tests included when required

---

## Additional Resources

- `purpose.md`: Detailed project purpose
- `structure.md`: Detailed project structure
- `development.md`: Development guidelines
- `README.md`: Assistant guidelines
