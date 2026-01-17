# subscription/models.py
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from subscriptions.utils.plan import PlanCode


class BaseModel(models.Model):
    created_at = models.DateTimeField(db_index=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SubscriptionPlan(BaseModel):
    """
    SubscriptionPlan = Pricing & Feature Definition

    mentality:
        - represents one pricing tier (Free, Standard, Business, Enterprise)
        - reusable across many tenants
        - mostly read-only after creation
    """

    # -------- Basic Info --------
    code = models.CharField(
        max_length=20,
        choices=PlanCode.choices,
        unique=True
    )

    price_npr = models.PositiveIntegerField(
        default=0,
        help_text="Price per user per month in NPR"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Can this plan be assigned to new tenants?"
    )

    # -------- Core Limits --------
    max_users = models.PositiveIntegerField(
        help_text="Maximum number of users allowed"
    )

    max_lead_forms = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum lead forms (null = unlimited)"
    )

    storage_gb_per_user = models.PositiveIntegerField(
        help_text="Storage per user in GB"
    )

    # -------- Communication --------
    bulk_email_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Monthly bulk email limit (null = unlimited)"
    )

    bulk_sms = models.BooleanField(
        default=False,
        help_text="Is bulk SMS enabled?"
    )

    # -------- Validation --------
    def clean(self):
        if self.price_npr < 0:
            raise ValidationError({"price_npr": "Price cannot be negative"})

        if self.max_users <= 0:
            raise ValidationError({"max_users": "Max users must be greater than 0"})

        if self.storage_gb_per_user <= 0:
            raise ValidationError(
                {"storage_gb_per_user": "Storage must be greater than 0"}
            )

    # -------- Properties --------
    @property
    def is_enabled(self):
        return self.is_active

    @property
    def display_name(self):
        return self.get_code_display()

    # -------- Meta --------
    """
        mentality: how should this model behave in DB?
        - ordering: cheaper plans first
        - index: active plans lookup
    """
    class Meta:
        ordering = ["price_npr"]
        verbose_name = "Subscription Plan"
        verbose_name_plural = "Subscription Plans"
        indexes = [
            models.Index(fields=["is_active"]),
            models.Index(fields=["code"]),
        ]

    def __str__(self):
        return f"{self.display_name} (NPR {self.price_npr})"