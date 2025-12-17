from django.shortcuts import render
from ledger.models import Account, JournalItem, ClosingPeriod

def profit_and_loss_report(request):
    # 🔹 Ambil daftar periode yang SUDAH di-closing
    closing_periods = ClosingPeriod.objects.filter(is_closed=True).order_by('-period')
    selected_period = request.GET.get('period')

    income_data = []
    expense_data = []
    total_income = 0
    total_expense = 0

    # Jika user pilih periode dan periode itu memang SUDAH CLOSED
    if selected_period and ClosingPeriod.objects.filter(period=selected_period, is_closed=True).exists():
        income_accounts = Account.objects.filter(account_type='INCOME', active=True)
        expense_accounts = Account.objects.filter(account_type='EXPENSES', active=True)

        # ==============================
        # 🔸 Pendapatan
        # ==============================
        for account in income_accounts:
            items = (
                JournalItem.objects
                .filter(account=account, journal_entry__period=selected_period)
                .select_related('journal_entry')
                .order_by('journal_entry__date', 'id')
            )

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

        # ==============================
        # 🔸 Pengeluaran
        # ==============================
        for account in expense_accounts:
            items = (
                JournalItem.objects
                .filter(account=account, journal_entry__period=selected_period)
                .select_related('journal_entry')
                .order_by('journal_entry__date', 'id')
            )

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

    # Jika belum pilih atau periode belum closed → semua kosong
    net_income = total_income - total_expense

    return render(request, 'ledger/profit_loss.html', {
        'income_data': income_data,
        'expense_data': expense_data,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_income': net_income,
        'closing_periods': closing_periods,
        'selected_period': selected_period,
    })
