from ledger.models import *
from ledger.admin import *
from .account import *
from .ledger_report import *


from django.contrib import admin
from django.utils import timezone
from ledger.models import ClosingPeriod


@admin.register(ClosingPeriod)
class ClosingPeriodAdmin(admin.ModelAdmin):
    list_display = ("period", "is_closed", "closed_by", "closed_at")
    list_filter = ("is_closed",)
    search_fields = ("period", "closed_by")
    ordering = ("-period",)
    readonly_fields = ("closed_at", "closed_by")

    actions = ["close_selected_periods"]

    @admin.action(description="🔒 Tutup periode yang dipilih")
    def close_selected_periods(self, request, queryset):
        """
        Custom action untuk menutup beberapa periode sekaligus dari admin.
        """
        closed_count = 0
        for period_obj in queryset:
            if not period_obj.is_closed:
                period_obj.close_period(user=request.user.username)
                closed_count += 1
        self.message_user(request, f"✅ {closed_count} periode berhasil ditutup.")

    def save_model(self, request, obj, form, change):
        """
        Jika admin menandai is_closed=True secara manual, otomatis jalankan close_period().
        """
        if change and not form.initial.get("is_closed") and obj.is_closed:
            obj.close_period(user=request.user.username)
        else:
            super().save_model(request, obj, form, change)
