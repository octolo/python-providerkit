## Project Purpose

**django-providerkit** is a Django library that provides integration for ProviderKit. It offers Django admin integration and utilities for managing providers in Django applications.

### Core Functionality

The library enables you to:

1. **Manage providers in Django admin**:
   - Display providers in Django admin interface
   - View provider metadata and configuration
   - Manage provider settings through Django admin
   - Use virtual models to represent providers without database tables

2. **Integrate ProviderKit with Django**:
   - Use ProviderKit providers in Django applications
   - Access provider information through Django models
   - Leverage ProviderKit's provider discovery and management
   - Use ProviderKit's configuration and validation features

3. **Virtual models for providers**:
   - `ProviderModel`: Virtual model representing providers
   - `ProviderkitModel`: Model for provider kits
   - `ServiceModel`: Model for provider services
   - No database tables required (uses VirtualQuerySet)

### Architecture

The library integrates ProviderKit with Django:

- Uses `VirtualModel` from django-virtualqueryset to represent providers
- Provides Django admin integration for provider management
- Maps ProviderKit's field definitions to Django model fields
- Uses ProviderKit's field descriptions and metadata

### Available Models

- **`ProviderModel`**: Virtual model for providers (inherits from `VirtualModel`)
- **`ProviderkitModel`**: Model for provider kits
- **`ServiceModel`**: Model for provider services

### Use Cases

- Display providers in Django admin interface
- Manage provider configuration through Django admin
- Integrate ProviderKit providers into Django applications
- View provider metadata and status in Django
- Build Django admin interfaces for provider management
