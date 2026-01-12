from django.contrib import admin
from django.utils.html import format_html
from .models import (
    TicketType,
    ParkingDailyReport,
    ParkingTicketItem,
    ParkingExpense,
    ParkingRevenueRule
)

# =========================
# Master Data
# =========================

@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(ParkingRevenueRule)
class ParkingRevenueRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'percentage', 'account', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)


# =========================
# Inline
# =========================

class ParkingTicketItemInline(admin.TabularInline):
    model = ParkingTicketItem
    extra = 1
    autocomplete_fields = ['ticket_type']
    readonly_fields = ('quantity_display', 'subtotal_display')

    def quantity_display(self, obj):
        if obj.pk:
            return obj.quantity()
        return "-"
    quantity_display.short_description = "Qty"

    def subtotal_display(self, obj):
        if obj.pk:
            return obj.subtotal()
        return "-"
    subtotal_display.short_description = "Subtotal"


class ParkingExpenseInline(admin.TabularInline):
    model = ParkingExpense
    extra = 1


# =========================
# Laporan Harian
# =========================

@admin.register(ParkingDailyReport)
class ParkingDailyReportAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'status',
        'total_bruto_display',
        'created_by',
        'posted_at'
    )
    list_filter = ('status', 'date')
    date_hierarchy = 'date'
    search_fields = ('date',)

    readonly_fields = (
        'status',
        'posted_at',
        'journal_entry_id',
        'total_bruto_display'
    )

    inlines = [
        ParkingTicketItemInline,
        ParkingExpenseInline
    ]

    fieldsets = (
        ("Informasi Laporan", {
            "fields": (
                'date',
                'created_by',
                'status',
                'posted_at',
                'journal_entry_id',
            )
        }),
        ("Ringkasan", {
            "fields": (
                'total_bruto_display',
            )
        }),
    )

    def total_bruto_display(self, obj):
        return obj.total_bruto()
    total_bruto_display.short_description = "Total Bruto"

    def has_delete_permission(self, request, obj=None):
        if obj and obj.status == 'posted':
            return False
        return super().has_delete_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if obj and obj.status == 'posted':
            return False
        return super().has_change_permission(request, obj)
