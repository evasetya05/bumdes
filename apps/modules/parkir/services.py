# apps/parking/services.py
from django.db import transaction
from django.utils import timezone
from decimal import Decimal

from apps.ledger.models import JournalEntry, JournalItem, Account
from .models import ParkingDailyReport, ParkingRevenueRule

def post_parking_daily_report(report_id):
    report = ParkingDailyReport.objects.select_for_update().get(id=report_id)

    if report.status == 'posted':
        raise ValueError("Report sudah diposting")

    with transaction.atomic():
        bruto = report.total_bruto()
        total_expense = sum(e.amount for e in report.expenses.all())

        # 1. Buat Journal Entry
        entry = JournalEntry.objects.create(
            date=report.date,
            description=f"Pendapatan Parkir {report.date}",
            reference_id=f"PARK-{report.id}"
        )

        # 2. Debit Kas
        kas_account = Account.objects.get(code='1101')
        JournalItem.objects.create(
            entry=entry,
            account=kas_account,
            debit=bruto - total_expense,
            credit=0
        )

        # 3. Kredit Pendapatan
        pendapatan_account = Account.objects.get(code='4101')
        JournalItem.objects.create(
            entry=entry,
            account=pendapatan_account,
            debit=0,
            credit=bruto
        )

        # 4. Pajak & Bagi Hasil
        for rule in ParkingRevenueRule.objects.filter(is_active=True):
            amount = bruto * (rule.percentage / Decimal('100'))

            JournalItem.objects.create(
                entry=entry,
                account=rule.account,
                debit=0,
                credit=amount
            )

        # 5. Finalisasi
        report.status = 'posted'
        report.journal_entry = entry
        report.posted_at = timezone.now()
        report.save()

    return entry
