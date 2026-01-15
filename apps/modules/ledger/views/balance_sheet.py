from django.shortcuts import render
from django.db.models import Sum
from ledger.models import Account, JournalItem, ClosingPeriod


# ==============================
# HITUNG SALDO AKUN
# ==============================
def calculate_balance(account, period=None, year=None):
    """
    Hitung saldo akun:
    - per periode (YYYY-MM)
    - atau per tahun (YYYY)
    """

    items = JournalItem.objects.filter(account=account, journal_entry__is_posted=True)

    if year:
        items = items.filter(journal_entry__date__year=year)
    elif period:
        items = items.filter(journal_entry__period=period)

    debit_total = items.aggregate(total=Sum('debit'))['total'] or 0
    credit_total = items.aggregate(total=Sum('credit'))['total'] or 0

    if account.balance_type == 'Debit':
        return debit_total - credit_total
    else:
        return credit_total - debit_total


# ==============================
# BALANCE SHEET VIEW
# ==============================
def balance_sheet_view(request):

    # ==========================
    # PARAMETER
    # ==========================
    mode = request.GET.get('mode', 'period')   # 'period' | 'year'
    selected_period = request.GET.get('period')
    selected_year = request.GET.get('year')

    # ==========================
    # DATA PERIODE
    # ==========================
    periods = ClosingPeriod.objects.all().order_by('-period')

    if mode == 'period':
        if not selected_period and periods.exists():
            selected_period = periods.first().period

    # ==========================
    # AKUN
    # ==========================
    asset_accounts = Account.objects.filter(account_type='ASSET', active=True)
    liability_accounts = Account.objects.filter(account_type='LIABILITY', active=True)
    equity_accounts = Account.objects.filter(account_type='CAPITAL', active=True)

    assets, liabilities, equities = [], [], []
    total_assets = total_liabilities = total_equities = 0

    # ==========================
    # HITUNG ASSET
    # ==========================
    for acc in asset_accounts:
        balance = calculate_balance(
            acc,
            period=selected_period if mode == 'period' else None,
            year=selected_year if mode == 'year' else None
        )
        assets.append({'account': acc, 'balance': balance})
        total_assets += balance

    # ==========================
    # HITUNG LIABILITY
    # ==========================
    for acc in liability_accounts:
        balance = calculate_balance(
            acc,
            period=selected_period if mode == 'period' else None,
            year=selected_year if mode == 'year' else None
        )
        liabilities.append({'account': acc, 'balance': balance})
        total_liabilities += balance

    # ==========================
    # HITUNG EQUITY
    # ==========================
    for acc in equity_accounts:
        balance = calculate_balance(
            acc,
            period=selected_period if mode == 'period' else None,
            year=selected_year if mode == 'year' else None
        )
        equities.append({'account': acc, 'balance': balance})
        total_equities += balance

    # ==========================
    # CONTEXT
    # ==========================
    context = {
        'mode': mode,
        'periods': periods,
        'selected_period': selected_period,
        'selected_year': selected_year,
        'assets': assets,
        'liabilities': liabilities,
        'equities': equities,
        'total_assets': total_assets,
        'total_liabilities': total_liabilities,
        'total_equities': total_equities,
        'total_liabilities_equities': total_liabilities + total_equities,
    }

    return render(request, 'ledger/balance_sheet.html', context)
