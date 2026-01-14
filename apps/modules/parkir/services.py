# apps/parking/services.py
from django.db import transaction
from django.utils import timezone
from decimal import Decimal

from apps.modules.ledger.models import JournalEntry, JournalItem, Account
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

        # 3. Kredit Pendapatan (Sesuai Akun di Item)
        revenue_map = {}
        for item in report.items.all():
            acct = item.revenue_account
            val = item.subtotal()
            revenue_map[acct] = revenue_map.get(acct, 0) + val

        for account, amount in revenue_map.items():
            JournalItem.objects.create(
                entry=entry,
                account=account,
                debit=0,
                credit=amount
            )

        # 3b. Debit Pengeluaran Operasional (Taken from Cash)
        # Entry: Dr. Expense, Cr. (Imisitly matched by reduced Dr. Kas)
        # Because Dr. Kas is (Rev - Exp). Total Dr = (Rev - Exp) + Exp = Rev.
        # Total Cr = Rev. Balanced.
        expense_map = {}
        for exp in report.expenses.all():
            acct = exp.expense_account
            expense_map[acct] = expense_map.get(acct, 0) + exp.amount

        for account, amount in expense_map.items():
            JournalItem.objects.create(
                entry=entry,
                account=account,
                debit=amount,
                credit=0
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
