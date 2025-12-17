from django import template
from ledger.models import ClosingPeriod

register = template.Library()

@register.filter
def closing_status(period):
    """Return True jika periode sudah closing, False jika belum atau tidak ditemukan."""
    if not period:
        return False
    cp = ClosingPeriod.objects.filter(period=period).first()
    return cp.is_closed if cp else False
