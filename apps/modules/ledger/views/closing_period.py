from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from ledger.models.closing_period import ClosingPeriod
from ledger.models import JournalEntry, JournalItem, Account


def closing_period_list(request):
    periods = ClosingPeriod.objects.all().order_by('-period')

    # 🔧 Jika belum ada data sama sekali, buat periode bulan sekarang
    if not periods.exists():
        current_period = timezone.now().strftime('%Y-%m')
        ClosingPeriod.objects.create(period=current_period, is_closed=False)
        messages.info(request, f"Periode awal {current_period} dibuat otomatis.")
        return redirect('closing_period_list')

    # Pastikan minimal satu periode open
    if not ClosingPeriod.objects.filter(is_closed=False).exists():
        current_period = timezone.now().strftime('%Y-%m')
        period_obj, created = ClosingPeriod.objects.get_or_create(period=current_period)
        if created:
            messages.info(request, f"Periode {current_period} dibuat otomatis sebagai periode aktif.")
        else:
            period_obj.is_closed = False
            period_obj.save()
        return redirect('closing_period_list')

    return render(request, 'ledger/closing_period_list.html', {'periods': periods})


# ==========================================================
# 🔒 CLOSE PERIOD
# ==========================================================
def close_period(request, period):
    """Menutup periode dan otomatis membuka periode berikutnya."""
    period_obj = ClosingPeriod.ensure_period_exists(period)

    if period_obj.is_closed:
        messages.warning(request, f"Periode {period} sudah tertutup.")
        return redirect('closing_period_list')

    # Tutup periode saat ini
    period_obj.is_closed = True
    period_obj.closed_at = timezone.now()
    period_obj.closed_by = request.user.username if request.user.is_authenticated else "system"
    period_obj.save()

    # ==========================================================
    # 🧾 PENYESUAIAN RETAINED EARNINGS (blok terpisah)
    # ==========================================================
    adjust_retained_earnings(request, period, request.user if request.user.is_authenticated else None)


    # ==========================================================
    # 🚪 Lanjut buka periode berikutnya
    # ==========================================================
    try:
        current_date = datetime.strptime(period, "%Y-%m")
        next_month = (current_date + relativedelta(months=1)).strftime("%Y-%m")
    except ValueError:
        messages.error(request, "Format periode tidak valid. Gunakan YYYY-MM.")
        return redirect('closing_period_list')

    next_period, created = ClosingPeriod.objects.get_or_create(period=next_month)
    if created or next_period.is_closed:
        next_period.is_closed = False
        next_period.closed_at = None
        next_period.closed_by = None
        next_period.save()
        messages.success(request, f"Periode {period} ditutup, periode {next_month} dibuka otomatis.")
    else:
        messages.info(request, f"Periode {period} ditutup. Periode {next_month} sudah aktif.")

    return redirect('closing_period_list')


# ==========================================================
# 📦 BLOK PENYESUAIAN RETAINED EARNINGS
# ==========================================================
from django.contrib import messages

def adjust_retained_earnings(request, period, user=None):
    """Hitung laba/rugi periode & sesuaikan akun retained earnings."""
    try:
        income_accounts = Account.objects.filter(account_type="INCOME")
        expense_accounts = Account.objects.filter(account_type="EXPENSES")

        total_income = (
            JournalItem.objects.filter(
                journal_entry__period=period, account__in=income_accounts
            ).aggregate(total=Sum('credit') - Sum('debit'))['total'] or 0
        )

        total_expense = (
            JournalItem.objects.filter(
                journal_entry__period=period, account__in=expense_accounts
            ).aggregate(total=Sum('debit') - Sum('credit'))['total'] or 0
        )

        net_profit = total_income - total_expense

        if net_profit == 0:
            messages.info(request, f"Tidak ada laba/rugi untuk periode {period}.")
            return

        retained_account = (
            Account.objects.filter(account_name__icontains="Retained Earnings").first()
            or Account.objects.filter(account_code="3999").first()
            or Account.objects.filter(account_type="CAPITAL").first()
        )

        if not retained_account:
            messages.warning(request, "⚠ Akun Retained Earnings tidak ditemukan.")
            return

        je = JournalEntry.objects.create(
            date=timezone.now().date(),
            description=f"Automatic Retained Earnings Adjustment for {period}",
            period=period,
            is_posted=True,
        )

        if net_profit > 0:
            JournalItem.objects.create(
                journal_entry=je,
                account=retained_account,
                credit=net_profit,
                note="Transfer Profit to Retained Earnings",
            )
        else:
            JournalItem.objects.create(
                journal_entry=je,
                account=retained_account,
                debit=abs(net_profit),
                note="Transfer Loss to Retained Earnings",
            )

        messages.success(request, f"✅ Retained earnings disesuaikan otomatis untuk periode {period}.")
        print(f"✅ Retained earnings adjusted: {net_profit}")

    except Exception as e:
        messages.error(request, f"Gagal menyesuaikan Retained Earnings: {e}")
