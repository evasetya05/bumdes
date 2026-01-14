import json

from django.shortcuts import get_object_or_404, render, redirect
from apps.modules.ledger.models import JournalEntry, JournalItem, Account, ClosingPeriod
from django.utils.timezone import now
from datetime import datetime
from django.contrib import messages

def create_journal_entry(request):
    if request.method == 'POST':
        try:
            date_str = request.POST.get('date')
            date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else now().date()
            description = request.POST.get('description', '').strip()
            report_id = request.POST.get('report_id')

            # Ambil periode open saat ini
            open_period = ClosingPeriod.get_open_period()
            period_now = open_period.period

            # Buat jurnal baru (akan otomatis pakai periode open saat ini)
            journal = JournalEntry.objects.create(date=date, description=description)

            # Jika user input tanggal beda bulan dari periode open, beri warning
            date_period = date.strftime("%Y-%m")
            if date_period != period_now:
                messages.warning(
                    request,
                    f"Tanggal jurnal {date_period} berbeda dari periode open ({period_now}). "
                    f"Transaksi dimasukkan ke periode {period_now}."
                )

            accounts = request.POST.getlist('account_id[]')
            debits = request.POST.getlist('debit[]')
            credits = request.POST.getlist('credit[]')
            notes = request.POST.getlist('note[]')

            for account_id, debit, credit, note in zip(accounts, debits, credits, notes):
                if not account_id.strip():
                    continue

                account = get_object_or_404(Account, pk=account_id)
                JournalItem.objects.create(
                    journal_entry=journal,
                    account=account,
                    debit=float(debit or 0),
                    credit=float(credit or 0),
                    note=note or ''
                )

            messages.success(request, f"Jurnal berhasil dibuat untuk periode {journal.period}.")
            if report_id:
                return redirect('parkir:report_detail', pk=report_id)
            return redirect('ledger:journal_list')

        except ValueError as e:
            messages.error(request, str(e))
            return redirect('journal_list')

    prefill = request.session.pop('journal_prefill', None)
    prefill_entries = prefill.get('entries', []) if prefill else []
    prefill_date = prefill.get('date') if prefill else now().date().strftime('%Y-%m-%d')
    prefill_description = prefill.get('description', '') if prefill else ''
    prefill_report_id = prefill.get('report_id') if prefill else ''
    prefill_entries_json = json.dumps(prefill_entries)

    context = {
        'today': now().date().strftime('%Y-%m-%d'),
        'accounts': Account.objects.all(),
        'prefill_entries_json': prefill_entries_json,
        'prefill_date': prefill_date,
        'prefill_description': prefill_description,
        'prefill_report_id': prefill_report_id,
    }

    return render(request, 'ledger/journal_entry.html', context)


def journal_list(request):
    # Ambil semua jurnal, urutkan berdasarkan periode dan tanggal
    journals = (
        JournalEntry.objects
        .order_by('-period', '-date', '-id')
        .prefetch_related('items', 'items__account')
    )

    # Kelompokkan berdasarkan periode
    grouped_journals = {}
    for j in journals:
        grouped_journals.setdefault(j.period or 'Tanpa Periode', []).append(j)

    context = {
        'grouped_journals': grouped_journals
    }
    return render(request, 'ledger/journal_list.html', context)