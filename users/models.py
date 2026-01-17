from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from tenant_users.tenants.models import UserProfile

class BaseModel(models.Model):
    created_at = models.DateTimeField(db_index=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CustomUser(UserProfile, BaseModel):
    """
    Custom User model with three user types:

    1. Superuser
       - System admin
       - Public tenant
       - No role

    2. Tenant Admin
       - Organization admin
       - Assigned to tenant via membership
       - No role

    3. Role-based User
       - Regular user
       - Assigned to tenant via membership
       - Has role
    """

    # ------------------------------------------------------------------
    # Role choices for role-based users
    # ------------------------------------------------------------------
    class RoleChoices(models.TextChoices):
        ADMISSION_OFFICER = "admission_officer", "Admission Officer"
        COUNSELOR = "counselor", "Counselor"
        MANAGER = "manager", "Manager"
        RECEPTIONIST = "receptionist", "Receptionist"
        MARKETING = "marketing", "Marketing"

    # ------------------------------------------------------------------
    # Core fields
    # ------------------------------------------------------------------
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    role = models.CharField(
        max_length=50,
        choices=RoleChoices.choices,
        null=True,
        blank=True,
        help_text="Role for role-based users",
    )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    def clean(self):
        errors = {}

        if not self.email:
            errors["email"] = "Email cannot be empty"
        if not self.username:
            errors["username"] = "Username cannot be empty"
        elif len(self.username) < 3:
            errors["username"] = "Username must be at least 3 characters long"
            
        if errors:
            raise ValidationError(errors)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_recent(self):
        return (timezone.now() - self.date_joined).days <= 7

    @property
    def role_display(self):
        return self.get_role_display() if self.role else None

    # ------------------------------------------------------------------
    # State helpers
    # ------------------------------------------------------------------
    def deactivate(self):
        self.is_active = False
        self.save(update_fields=["is_active", "updated_at"])
        return self

    def activate(self):
        self.is_active = True
        self.save(update_fields=["is_active", "updated_at"])
        return self

    def create_admin(self):
        self.is_staff = True 
        self.is_superuser = True 
        self.save(update_fields=["is_staff", "is_superuser", "updated_at"])
        return self  
    
    def create_role_based_user(self, role):
        self.is_staff = False
        self.is_superuser = False
        self.save(update_fields=["is_staff", "is_superuser"])
        return self


    # ------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------
    class Meta:
        ordering = ["-created_at"]
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=["is_active"]),
            models.Index(fields=["role"]),
        ]

    def __str__(self):
        return self.email
