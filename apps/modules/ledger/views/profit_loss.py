from django.shortcuts import render
from apps.modules.ledger.models import Account, JournalItem, ClosingPeriod


def profit_and_loss_report(request):
    """
    Profit & Loss:
    - mode=period → per periode closing (bulanan)
    - mode=year   → per tahun
    """

    # ==========================
    # PARAMETER
    # ==========================
    mode = request.GET.get('mode', 'period')   # 'period' | 'year'
    selected_period = request.GET.get('period')
    selected_year = request.GET.get('year')

    income_data = []
    expense_data = []
    total_income = 0
    total_expense = 0

    # ==========================
    # DATA PERIODE
    # ==========================
    closing_periods = ClosingPeriod.objects.filter(is_closed=True).order_by('-period')

    if mode == 'period':
        if not selected_period and closing_periods.exists():
            selected_period = closing_periods.first().period

        # validasi: hanya boleh periode closed
        if not ClosingPeriod.objects.filter(period=selected_period, is_closed=True).exists():
            selected_period = None

    # ==========================
    # AKUN
    # ==========================
    income_accounts = Account.objects.filter(account_type='INCOME', active=True)
    expense_accounts = Account.objects.filter(account_type='EXPENSES', active=True)

    # ==========================
    # FILTER TRANSAKSI
    # ==========================
    def get_items(account):
        qs = JournalItem.objects.filter(
            account=account,
            journal_entry__is_posted=True
        ).select_related('journal_entry').order_by('journal_entry__date', 'id')

        if mode == 'year' and selected_year:
            qs = qs.filter(journal_entry__date__year=selected_year)
        elif mode == 'period' and selected_period:
            qs = qs.filter(journal_entry__period=selected_period)
        else:
            qs = qs.none()

        return qs

    # ==========================
    # PENDAPATAN
    # ==========================
    for account in income_accounts:
        items = get_items(account)

        balance = 0
        rows = []
        for item in items:
            balance += item.credit or 0
            rows.append({
                'date': item.journal_entry.date,
                'desc': item.journal_entry.description,
                'debit': item.debit,
                'credit': item.credit,
                'balance': balance,
            })

        subtotal = sum(item.credit or 0 for item in items)
        total_income += subtotal

        income_data.append({
            'account': account,
            'rows': rows,
            'subtotal': subtotal,
        })

    # ==========================
    # BEBAN
    # ==========================
    for account in expense_accounts:
        items = get_items(account)

        balance = 0
        rows = []
        for item in items:
            balance += (item.debit or 0) - (item.credit or 0)
            rows.append({
                'date': item.journal_entry.date,
                'desc': item.journal_entry.description,
                'debit': item.debit,
                'credit': item.credit,
                'balance': balance,
            })

        total_debit = sum(item.debit or 0 for item in items)
        total_credit = sum(item.credit or 0 for item in items)
        subtotal = total_debit - total_credit
        total_expense += subtotal

        expense_data.append({
            'account': account,
            'rows': rows,
            'subtotal': subtotal,
        })

    # ==========================
    # LABA BERSIH
    # ==========================
    net_income = total_income - total_expense

    # ==========================
    # RENDER
    # ==========================
    return render(request, 'ledger/profit_loss.html', {
        'mode': mode,
        'selected_period': selected_period,
        'selected_year': selected_year,
        'closing_periods': closing_periods,
        'income_data': income_data,
        'expense_data': expense_data,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_income': net_income,
    })
