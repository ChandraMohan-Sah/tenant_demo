import json
from django.core.management import BaseCommand, call_command
from django.conf import settings
from django.utils import timezone
from django_tenants.utils import schema_context

from tenant.models import Tenant, Domain
from users.models import CustomUser
from subscriptions.models import SubscriptionPlan
from todo.models import Task


class Command(BaseCommand):
    help = "Create tenants, tenant admins, role-based users, and optionally dummy tasks"
    tenants_file = "tenant/data/tenants.json"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open(self.tenants_file) as f:
            self.tenants = json.load(f)

    def handle(self, *args, **kwargs):
        # Ensure all migrations are applied
        call_command("migrate", interactive=False)

        # Step 1: Create tenants
        for data in self.tenants:
            tenant = self.create_tenant(data)

            # Step 2: Create tenant admin
            self.create_tenant_admin(tenant, data["owner"])

        self.stdout.write(
            self.style.SUCCESS("✅ Tenants and admins created successfully")
        )
    
    # ==================================================
    # STEP 1: CREATE TENANT
    # ==================================================
    def create_tenant(self, data):
        tenant, created = Tenant.objects.get_or_create(
            schema_name=data["schema_name"],
            defaults={
                "name": data["name"],
                "slug": data["slug"],
                "is_active": data.get("is_active", True),
            },
        )

        # Attach subscription plan (default to free)
        plan_code = data.get("plan") or "free"
        plan = SubscriptionPlan.objects.get(code=plan_code)
        tenant.plan = plan
        tenant.save(update_fields=["plan"])

        # Create domain
        domain_name = settings.BASE_DOMAIN
        if data.get("subdomain"):
            domain_name = f"{data['subdomain']}.{settings.BASE_DOMAIN}"

        Domain.objects.get_or_create(
            tenant=tenant,
            domain=domain_name,
            defaults={"is_primary": data["schema_name"] == settings.PUBLIC_SCHEMA_NAME},
        )

        return tenant

    # ==================================================
    # STEP 2: CREATE TENANT ADMIN
    # ==================================================
    def create_tenant_admin(self, tenant, owner_data):
        """
        Creates a tenant admin. For public tenant, this could be a global superuser.
        """
        user, created = CustomUser.objects.get_or_create(
            email=owner_data["email"],
            defaults={
                "phone_number": owner_data.get("phone_number"),
                "role": owner_data.get("role"),
            },
        )

        if created:
            user.set_password(owner_data["password"])
            user.save()

        # Attach tenant if the model has tenant field
        if hasattr(user, "tenant") and getattr(user, "tenant", None) != tenant:
            user.tenant = tenant
            user.save(update_fields=["tenant"])

        return user

    # ==================================================
    # STEP 3: CREATE ROLE-BASED USER
    # ==================================================
    def create_role_user(self, tenant, user_data): 
        """
        user_data = {
            "email": "staff@demo1.localhost",
            "password": "password",
            "role": "counselor",
            "phone_number": "optional",
        }
        """
        user, created = CustomUser.objects.get_or_create(
            email=user_data["email"],
            defaults={
                "role": user_data.get("role"),
                "phone_number": user_data.get("phone_number"),
            },
        )

        if created:
            user.set_password(user_data["password"])
            user.save()

        # Attach tenant
        if hasattr(user, "tenant") and getattr(user, "tenant", None) != tenant:
            user.tenant = tenant
            user.save(update_fields=["tenant"])

        return user

    # ==================================================
    # STEP 4: CREATE DUMMY TASKS
    # ==================================================
    def create_dummy_tasks(self):
        for data in self.tenants:
            if data["schema_name"] == settings.PUBLIC_SCHEMA_NAME:
                continue

            with schema_context(data["schema_name"]):
                user = CustomUser.objects.get(email=data["owner"]["email"])

                if Task.objects.exists():
                    continue

                tasks = [
                    Task(
                        user=user,
                        title="Setup project",
                        description="Initialize tenant project structure",
                        completed=True,
                        published_at=timezone.now(),
                    ),
                    Task(
                        user=user,
                        title="Create APIs",
                        description="Build CRUD APIs for tasks",
                        completed=False,
                    ),
                    Task(
                        user=user,
                        title="Deploy app",
                        description="Deploy tenant application to server",
                        completed=False,
                    ),
                ]

                for task in tasks:
                    task.full_clean()
                    task.save()
