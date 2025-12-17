from django.shortcuts import render
from django.db.models import Sum
from ledger.models import Account, JournalItem, ClosingPeriod


def calculate_balance(account, period=None):
    """Hitung saldo akun berdasarkan periode (YYYY-MM)."""
    items = JournalItem.objects.filter(account=account)

    if period:
        # Filter berdasarkan periode di JournalEntry
        items = items.filter(journal_entry__period=period)

    debit_total = items.aggregate(total=Sum('debit'))['total'] or 0
    credit_total = items.aggregate(total=Sum('credit'))['total'] or 0

    if account.balance_type == 'Debit':
        return debit_total - credit_total
    else:
        return credit_total - debit_total


def balance_sheet_view(request):
    # 🔹 Ambil semua periode dari ClosingPeriod
    periods = ClosingPeriod.objects.all().order_by('-period')

    # 🔹 Periode dipilih dari dropdown (GET ?period=YYYY-MM)
    selected_period = request.GET.get('period')
    if not selected_period and periods.exists():
        selected_period = periods.first().period  # default: periode terbaru

    # 🔹 Ambil akun berdasarkan jenis
    asset_accounts = Account.objects.filter(account_type='ASSET', active=True)
    liability_accounts = Account.objects.filter(account_type='LIABILITY', active=True)
    equity_accounts = Account.objects.filter(account_type='CAPITAL', active=True)

    assets, liabilities, equities = [], [], []
    total_assets = total_liabilities = total_equities = 0

    # 🔹 Hitung aset
    for acc in asset_accounts:
        balance = calculate_balance(acc, selected_period)
        assets.append({'account': acc, 'balance': balance})
        total_assets += balance

    # 🔹 Hitung kewajiban
    for acc in liability_accounts:
        balance = calculate_balance(acc, selected_period)
        liabilities.append({'account': acc, 'balance': balance})
        total_liabilities += balance

    # 🔹 Hitung ekuitas
    for acc in equity_accounts:
        balance = calculate_balance(acc, selected_period)
        equities.append({'account': acc, 'balance': balance})
        total_equities += balance

    context = {
        'periods': periods,
        'selected_period': selected_period,
        'assets': assets,
        'liabilities': liabilities,
        'equities': equities,
        'total_assets': total_assets,
        'total_liabilities': total_liabilities,
        'total_equities': total_equities,
        'total_liabilities_equities': total_liabilities + total_equities,
    }

    return render(request, 'ledger/balance_sheet.html', context)
