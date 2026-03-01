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

Each package has its own `service.py` and development workflow:

```bash
# In python-providerkit/ or django-providerkit/
./service.py dev install-dev
./service.py dev test
./service.py quality lint
```

## License

MIT
