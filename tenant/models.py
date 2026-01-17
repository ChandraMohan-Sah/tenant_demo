# # tenants/models.py
# from django.contrib.auth.models import AbstractUser
# from django.db import models
# from django_tenants.models import TenantMixin, DomainMixin


# class Tenant(TenantMixin):
#     name = models.CharField(max_length=100)


# class Domain(DomainMixin):
#     pass


from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from subscriptions.models import SubscriptionPlan   # import plan
from django_tenants.models import TenantMixin , DomainMixin 


class BaseModel(models.Model):
    created_at = models.DateTimeField(db_index=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Tenant(TenantMixin, BaseModel): 
    """
    Tenant = Workspace / Organization
    Using django-tenants for schema-based multi-tenancy
    """

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)

    # -------- Subscription (optional) -------- 
    plan = models.ForeignKey(
        SubscriptionPlan,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tenants",
    )

    # auto_create_schema = True  # important, creates schema automatically 

    # -------- validation ----------
    def clean(self):
        if not self.name:
            raise ValidationError({"name": "Tenant name cannot be empty"})
        if not self.slug:
            raise ValidationError({"slug": "Tenant slug cannot be empty"})
        if len(self.name) < 3:
            raise ValidationError(
                {"name": "Tenant name must be at least 3 characters long"}
            )

    # -------- properties ----------
    @property
    def is_enabled(self):
        return self.is_active

    @property
    def display_name(self):
        return self.name.title()

    @property
    def has_subscription(self):
        return self.plan is not None

    # -------- methods ----------
    def deactivate(self):
        self.is_active = False
        self.updated_at = timezone.now()
        self.save()
        return self

    def activate(self):
        self.is_active = True
        self.updated_at = timezone.now()
        self.save()
        return self

    def attach_free_plan(self):
        self.plan = SubscriptionPlan.objects.get(code="free")
        self.save()
        return self 
    
    def attach_plan(self, plan):
        """Attach or change subscription plan"""
        self.plan = plan
        self.updated_at = timezone.now()
        # go to payment function 
        self.save()
        return self

    # -------- Meta ----------
    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"
        indexes = [
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.name

class Domain(DomainMixin, BaseModel):
    """
    Domain model for django-tenants
    Maps domain names to tenant schemas
    """

    def clean(self):
        # Ensure domain is not empty
        if not self.domain:
            raise ValidationError({"domain": "Domain cannot be empty"})

    def __str__(self):
        return f"{self.domain} ({'primary' if self.is_primary else 'secondary'})"
    