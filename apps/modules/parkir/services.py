# apps/parking/services.py
from django.db import transaction
from django.utils import timezone
from decimal import Decimal

from apps.modules.ledger.models import JournalEntry, JournalItem, Account
from .models import ParkingDailyReport, ParkingRevenueRule

def get_default_cash_account():
    cash_account = Account.objects.filter(coa_role_default__iexact='cash').first()
    if cash_account:
        return cash_account

    cash_account = Account.objects.filter(account_type__iexact='ASSET').first()
    if cash_account:
        return cash_account

    raise Account.DoesNotExist("Tidak menemukan akun kas (coa_role_default='cash' atau account_type='ASSET')")


def prepare_journal_prefill(report: ParkingDailyReport):
    cash_warning = None
    try:
        cash_account = get_default_cash_account()
    except Account.DoesNotExist:
        cash_account = None
        cash_warning = "Akun kas default tidak ditemukan. Pilih akun kas secara manual sebelum menyimpan jurnal."

    revenue_map = {}
    for item in report.items.all():
        amount = Decimal(item.subtotal() or 0)
        if amount <= 0:
            continue
        revenue_map[item.revenue_account] = revenue_map.get(item.revenue_account, Decimal('0')) + amount

    expense_entries = []
    total_expense = Decimal('0')
    for expense in report.expenses.all():
        amount = Decimal(expense.amount or 0)
        if amount <= 0:
            continue
        total_expense += amount
        expense_entries.append((expense.expense_account, amount, expense.description))

    total_revenue = sum(revenue_map.values(), Decimal('0'))

    entries = []

    def add_entry(account, amount, note="", force_side=None):
        if not account or amount <= 0:
            return

        balance_type = (account.balance_type or '').upper()
        side = (force_side or balance_type or '').upper()

        debit = Decimal('0')
        credit = Decimal('0')

        if side == 'CREDIT':
            credit = amount
        elif side == 'DEBIT':
            debit = amount
        else:
            # fallback gunakan debit
            debit = amount

        entries.append({
            'account_id': account.id,
            'debit': float(debit),
            'credit': float(credit),
            'note': note or ""
        })

    if total_revenue > 0:
        add_entry(cash_account, total_revenue, "Setoran pendapatan parkir", force_side='DEBIT')

    for account, amount in revenue_map.items():
        add_entry(account, amount, f"Pendapatan dari {report.date}", force_side='CREDIT')

    if total_expense > 0:
        for account, amount, description in expense_entries:
            add_entry(account, amount, description, force_side='DEBIT')
        add_entry(cash_account, total_expense, "Pengeluaran operasional parkir", force_side='CREDIT')

    return {
        'entries': entries,
        'cash_warning': cash_warning,
        'total_revenue': float(total_revenue),
        'total_expense': float(total_expense),
    }


def post_parking_daily_report(report_id):
    with transaction.atomic():
        report = ParkingDailyReport.objects.select_for_update().get(id=report_id)

        if report.status == 'posted':
            raise ValueError("Report sudah diposting")

        bruto = Decimal(report.total_bruto() or 0)
        if bruto <= 0:
            raise ValueError("Total pendapatan (bruto) masih 0.")

        cash_account = get_default_cash_account()

        revenue_map = {}
        for item in report.items.all():
            amount = Decimal(item.subtotal() or 0)
            if amount <= 0:
                continue
            revenue_map[item.revenue_account] = revenue_map.get(item.revenue_account, Decimal('0')) + amount

        total_revenue = sum(revenue_map.values(), Decimal('0'))
        if total_revenue <= 0:
            raise ValueError("Tidak ada item pendapatan yang valid untuk diposting.")

        total_expense = Decimal('0')
        expense_entries = []
        for expense in report.expenses.all():
            amount = Decimal(expense.amount or 0)
            if amount <= 0:
                continue
            total_expense += amount
            expense_entries.append((expense.expense_account, amount, expense.description))

        # 1. Buat Journal Entry
        entry = JournalEntry.objects.create(
            date=report.date,
            description=f"Pendapatan Parkir {report.date}"
        )

        # 2. Debit Kas untuk total pendapatan
        JournalItem.objects.create(
            journal_entry=entry,
            account=cash_account,
            debit=total_revenue,
            credit=Decimal('0'),
            note="Setoran pendapatan parkir"
        )

        # 3. Kredit Pendapatan sesuai akun
        for account, amount in revenue_map.items():
            JournalItem.objects.create(
                journal_entry=entry,
                account=account,
                debit=Decimal('0'),
                credit=amount,
                note=f"Pendapatan dari {report.date}"
            )

        # 4. Catat pengeluaran operasional (Debit beban, Kredit Kas)
        if total_expense > 0:
            for account, amount, description in expense_entries:
                JournalItem.objects.create(
                    journal_entry=entry,
                    account=account,
                    debit=amount,
                    credit=Decimal('0'),
                    note=description or ""
                )

            JournalItem.objects.create(
                journal_entry=entry,
                account=cash_account,
                debit=Decimal('0'),
                credit=total_expense,
                note="Pengeluaran operasional parkir"
            )

        # TODO: Tangani ParkingRevenueRule bila diperlukan (misalnya bagi hasil/pajak)

        # 5. Finalisasi
        report.status = 'posted'
        report.journal_entry_id = entry.id
        report.posted_at = timezone.now()
        report.save()

    return entry
