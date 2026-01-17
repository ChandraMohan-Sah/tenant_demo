from django.contrib import admin
from .models import SubscriptionPlan


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    # -------- List View --------
    list_display = (
        "display_name",
        "price_npr",
        "max_users",
        "storage_gb_per_user",
        "bulk_sms",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
        "bulk_sms",
    )

    ordering = ("price_npr",)
