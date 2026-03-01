## Project Structure

django-providerkit follows a standard Python package structure with Django integration for ProviderKit.

### General Structure

```
django-providerkit/
├── src/
│   └── django_providerkit/        # Main package directory
│       ├── __init__.py       # Package exports and field associations
│       ├── models/           # Django model definitions
│       │   ├── __init__.py   # Model exports
│       │   ├── provider.py  # ProviderModel
│       │   └── service.py    # ServiceModel
│       ├── managers/         # Custom managers
│       │   ├── __init__.py   # Manager exports
│       │   ├── provider.py   # ProviderManager
│       │   └── service.py    # ServiceManager
│       ├── admin/            # Django admin configuration
│       │   ├── __init__.py   # Admin exports
│       │   ├── provider.py   # Provider admin
│       │   └── service.py    # Service admin
│       ├── views/            # Django views
│       │   ├── __init__.py   # View exports
│       │   └── provider.py  # Provider views
│       ├── urls.py           # URL configuration
│       └── apps.py            # Django app configuration
├── tests/                    # Test suite
│   └── ...
├── docs/                     # Documentation
│   └── ...
├── service.py                # Main service entry point script
├── pyproject.toml            # Project configuration
└── ...
```

### Module Organization Principles

- **Single Responsibility**: Each module should have a clear, single purpose
- **Separation of Concerns**: Keep different concerns in separate modules
- **Django Integration**: Integrates ProviderKit with Django's ORM and admin
- **Virtual Models**: Uses VirtualQuerySet for provider representation
- **Clear Exports**: Use `__init__.py` to define public API

### Model Organization

The `models/` directory contains Django model definitions:

- **`provider.py`**: Defines `ProviderModel` - virtual model for providers
- **`service.py`**: Defines `ServiceModel` - virtual model for provider services
- Models inherit from `VirtualModel` (no database tables)
- Field definitions come from ProviderKit's field metadata

### Manager Organization

The `managers/` directory contains custom managers:

- **`provider.py`**: `ProviderManager` - manager for provider models
- **`service.py`**: `ServiceManager` - manager for service models
- Managers handle data loading from ProviderKit

### Admin Organization

The `admin/` directory contains Django admin configurations:

- **`provider.py`**: Admin configuration for ProviderModel
- **`service.py`**: Admin configuration for ServiceModel
- Provides Django admin interface for viewing and managing providers

### Package Exports

The public API is defined in `src/django_providerkit/__init__.py`:
- `fields_associations`: Mapping of field types to Django model fields
- Models: Import from `django_providerkit.models`
- Admin: Import from `django_providerkit.admin`

### ProviderKit Integration

django-providerkit integrates ProviderKit with Django:
- Uses ProviderKit's field definitions (`FIELDS_PROVIDER_BASE`, `FIELDS_CONFIG_BASE`, etc.)
- Maps ProviderKit fields to Django model fields
- Uses VirtualQuerySet to represent providers without database tables
- Provides Django admin interface for ProviderKit providers
