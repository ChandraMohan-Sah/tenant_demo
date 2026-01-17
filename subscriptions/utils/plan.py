# subscription/plans.py
from django.db import models

class PlanCode(models.TextChoices):
    FREE = "free", "Free"
    STANDARD = "standard", "Standard"
    BUSINESS = "business", "Business"
    ENTERPRISE = "enterprise", "Enterprise"