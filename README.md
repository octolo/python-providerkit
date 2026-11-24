# ProviderKit

Monorepo containing **providerkit** (Python library for provider management) and **django-providerkit** (Django integration).

## Packages

### providerkit — `python-providerkit/`

Generic provider management library for Python. Provides a standardized way to manage, discover, and interact with multiple service providers in a unified manner.

- **Mixin-based architecture**: PackageMixin, ConfigMixin, ServiceMixin, UrlsMixin
- **Provider discovery**: From JSON, configuration, or directory scanning
- **CLI system**: Flexible command discovery
- **Use cases**: Multi-provider integrations (email, SMS, payment), fallback mechanisms, provider selection

📁 Details: [python-providerkit/README.md](python-providerkit/README.md) | Docs: [python-providerkit/docs/](python-providerkit/docs/)

### django-providerkit — `django-providerkit/`

Django interface for ProviderKit. Integrates providerkit into Django applications with admin interface and virtual models.

- **Django admin**: Display and manage providers in Django admin
- **Virtual models**: ProviderModel, ProviderkitModel, ServiceModel (no database tables)
- **Field mapping**: Automatic mapping of ProviderKit fields to Django model fields
- **Dependency**: Requires providerkit

📁 Details: [django-providerkit/README.md](django-providerkit/README.md) | Docs: [django-providerkit/docs/](django-providerkit/docs/)

## Repository Structure

```
providerkit/
├── python-providerkit/     # Core library
│   ├── src/providerkit/
│   ├── docs/
│   └── ...
├── django-providerkit/     # Django integration
│   ├── src/django_providerkit/
│   ├── docs/
│   └── ...
└── README.md               # This file
```

## Development

CI also audits dependencies and runs Bandit separately for each package.
Bandit findings in the Python package are reported without blocking pending
review.

Each package has its own `service.py` and development workflow:

```bash
# In python-providerkit/ or django-providerkit/
./service.py dev install-dev
./service.py dev test
./service.py quality lint
```

## License

MIT

## Local audit

Install the project's development/test dependencies (including both local
packages where applicable), plus the audit tools:

```bash
python -m pip install ruff mypy bandit pip-audit vulture radon xenon pytest pytest-django pytest-cov build twine
make audit
```

The Ruff profile requires version `0.17.5`: install it with
`python -m pip install ruff==0.17.5`.

Use the activated environment's Python, or pass `make audit PYTHON=/path/to/python`.
On systems without Make, run `python scripts/audit.py` directly. Git is required;
the geoaddress widget tests also require Node.js. The audit reports missing test
suites and runs all available checks even when earlier checks fail.
Xenon checks the absolute C, module B, and average A complexity thresholds. Existing
lint, typing, security, dependency, or test findings can make the audit fail.
CI also runs this audit as a non-blocking job and separately reports Radon maintainability without imposing a threshold.
