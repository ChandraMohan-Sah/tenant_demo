# tenants/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django_tenants.models import TenantMixin, DomainMixin




class Tenant(TenantMixin):
    name = models.CharField(max_length=100)


class Domain(DomainMixin):
    pass
