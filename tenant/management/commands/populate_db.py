import json
from django.core.management import BaseCommand, call_command
from django.conf import settings
from django.utils import timezone
from django_tenants.utils import schema_context

from tenant.models import Tenant, Domain
from users.models import CustomUser
from todo.models import Task


class Command(BaseCommand):
    help = "Create tenants, users and tenant-specific dummy tasks (safe, no DB drop)"

    tenants_file = "tenant/data/tenants.json"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open(self.tenants_file) as f:
            self.tenants = json.load(f)

    def handle(self, *args, **kwargs):
        # Run migrations first (Django will create schemas as needed)
        call_command("migrate", interactive=False)

        # Create tenants, domains, and superusers
        self.create_tenants()

        # Populate tenant-specific tasks
        self.create_dummy_tasks()

        self.stdout.write(
            self.style.SUCCESS("✅ Database populated successfully (no DB drop)")
        )

    # --------------------------------------------------
    # TENANTS + DOMAINS + USERS (PUBLIC SCHEMA)
    # --------------------------------------------------
    def create_tenants(self):
        for data in self.tenants:
            # Check if tenant already exists (idempotent)
            tenant, created = Tenant.objects.get_or_create(
                schema_name=data["schema_name"],
                defaults={"name": data["name"], "id": data["id"]},
            )

            # Create domain if not exists
            domain_str = settings.BASE_DOMAIN
            if data["subdomain"]:
                domain_str = f"{data['subdomain']}.{settings.BASE_DOMAIN}"

            Domain.objects.get_or_create(
                tenant=tenant,
                domain=domain_str,
                defaults={"is_primary": data["schema_name"] == settings.PUBLIC_SCHEMA_NAME},
            )

            # Create tenant superuser if not exists
            if not CustomUser.objects.filter(username=data["owner"]["username"]).exists():
                CustomUser.objects.create_superuser(
                    username=data["owner"]["username"],
                    email=data["owner"]["email"],
                    password=data["owner"]["password"],
                )

    # --------------------------------------------------
    # TENANT-SPECIFIC DUMMY TASKS
    # --------------------------------------------------
    def create_dummy_tasks(self):
        for data in self.tenants:
            # Skip public schema
            if data["schema_name"] == settings.PUBLIC_SCHEMA_NAME:
                continue

            with schema_context(data["schema_name"]):
                user = CustomUser.objects.get(username=data["owner"]["username"])

                # Check if tasks already exist
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
                    task.full_clean()  # validation
                    task.save()
