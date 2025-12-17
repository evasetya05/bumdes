from django.shortcuts import render
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db.models import Sum, F, Value
from django.db.models.functions import Coalesce
from ledger.models import Account, JournalItem, ClosingPeriod

def ledger_report(request):
    """
    Ledger report berdasarkan periode akuntansi (bukan tanggal jurnal).
    Menampilkan semua akun, termasuk yang tidak ada transaksi,
    dengan saldo awal & akhir jika ada.
    """
    selected_period = request.GET.get('period')
    ledger_data = []

    closed_periods = ClosingPeriod.objects.filter(is_closed=True).order_by('-period')
    open_periods = list(
        ClosingPeriod.objects.filter(is_closed=False).values_list('period', flat=True)
    )

    # Jika user tidak pilih periode → tampilkan periode open terakhir
    if not selected_period and open_periods:
        selected_period = open_periods[0]

    # Cari periode closed terakhir sebelum periode terpilih
    previous_closed = (
        ClosingPeriod.objects.filter(is_closed=True, period__lt=selected_period)
        .order_by('-period')
        .first()
    )
    previous_closed_period = previous_closed.period if previous_closed else None

    accounts = Account.objects.all().order_by('account_name')

    for account in accounts:
        # Filter transaksi hanya untuk periode terpilih
        items = (
            JournalItem.objects
            .filter(
                account=account,
                journal_entry__period=selected_period,
                journal_entry__is_posted=True   # ⬅️ Tambahan ini saja
            )
            .select_related('journal_entry')
            .order_by('journal_entry__date', 'id')
        )

        # 💰 Hitung saldo awal
        if previous_closed_period:
            opening_balance_qs = (
                JournalItem.objects.filter(
                    account=account,
                    journal_entry__period__lte=previous_closed_period,
                    journal_entry__is_posted=True   # ⬅️ Tambahan ini juga
                )
                .aggregate(total=Coalesce(Sum(F('debit') - F('credit')), Value(0)))
            )
            opening_balance = opening_balance_qs['total'] or 0
        else:
            opening_balance = 0

        balance = opening_balance

        # 🧾 Detail transaksi
        rows = []
        for item in items:
            balance += item.debit - item.credit
            rows.append({
                'date': item.journal_entry.date,
                'desc': item.journal_entry.description,
                'debit': intcomma(int(item.debit)),
                'credit': intcomma(int(item.credit)),
                'balance': intcomma(int(balance)),
            })

        # ✅ Tambahkan semua akun, meskipun kosong
        ledger_data.append({
            'account': account,
            'rows': rows,
            'opening_balance': intcomma(int(opening_balance)),
            'closing_balance': intcomma(int(balance)),
        })

    return render(request, 'ledger/ledger_report.html', {
        'ledger_data': ledger_data,
        'selected_period': selected_period,
        'closed_periods': closed_periods,
    })
