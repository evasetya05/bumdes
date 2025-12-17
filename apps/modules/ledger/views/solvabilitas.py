from django.shortcuts import render
from ledger.models import Account, JournalItem, ClosingPeriod

def get_balance_by_prefix(prefixes, period):
    """
    Hitung total saldo akun-akun dengan prefix tertentu.
    Prefix bisa berupa string ('1') atau list ['1010', '1100']
    """
    if isinstance(prefixes, str):
        prefixes = [prefixes]

    accounts = Account.objects.all()
    total = 0
    detail = []

    for acc in accounts:
        code = acc.coa if acc.coa and acc.coa != "Default CoA" else acc.account_name.split(':')[0].strip()
        if not any(code.startswith(p) for p in prefixes):
            continue

        items = JournalItem.objects.filter(journal_entry__period=period, account=acc)
        debit = sum(i.debit for i in items)
        credit = sum(i.credit for i in items)
        balance = debit - credit if acc.balance_type == 'Debit' else credit - debit

        total += balance
        detail.append({'coa': code, 'name': acc.account_name, 'balance': round(balance, 2)})

    return total, detail


def solvabilitas_view(request):
    """Tampilkan rasio solvabilitas & likuiditas + breakdown detail akun."""
    closed_periods = ClosingPeriod.objects.filter(is_closed=True).order_by('-period')
    selected_period = request.GET.get('period')

    if not selected_period and closed_periods.exists():
        selected_period = closed_periods.first().period

    if not selected_period:
        return render(request, 'ledger/solvabilitas.html', {'error': 'Belum ada periode yang ditutup.'})

    # === Ambil saldo-saldo utama ===
    aset_lancar, aset_lancar_detail = get_balance_by_prefix(['1'], selected_period)
    kewajiban_lancar, kewajiban_detail = get_balance_by_prefix(['2'], selected_period)
    ekuitas, ekuitas_detail = get_balance_by_prefix(['3'], selected_period)
    persediaan, persediaan_detail = get_balance_by_prefix(['1200'], selected_period)
    total_aset = aset_lancar
    total_kewajiban = kewajiban_lancar
    total_ekuitas = ekuitas

    # === Hitung rasio ===
    rasio_lancar = aset_lancar / total_kewajiban if total_kewajiban else 0
    rasio_cepat = (aset_lancar - persediaan) / total_kewajiban if total_kewajiban else 0
    rasio_utang_aset = total_kewajiban / total_aset if total_aset else 0
    rasio_utang_modal = total_kewajiban / total_ekuitas if total_ekuitas else 0
    rasio_ekuitas_aset = total_ekuitas / total_aset if total_aset else 0

    context = {
        'periods': closed_periods,
        'period': selected_period,
        # Nilai utama
        'rasio_lancar': round(rasio_lancar, 2),
        'rasio_cepat': round(rasio_cepat, 2),
        'rasio_utang_aset': round(rasio_utang_aset, 2),
        'rasio_utang_modal': round(rasio_utang_modal, 2),
        'rasio_ekuitas_aset': round(rasio_ekuitas_aset, 2),
        # Rincian pendukung
        'aset_lancar': round(aset_lancar, 2),
        'kewajiban_lancar': round(kewajiban_lancar, 2),
        'persediaan': round(persediaan, 2),
        'ekuitas': round(ekuitas, 2),
        'aset_lancar_detail': aset_lancar_detail,
        'kewajiban_detail': kewajiban_detail,
        'persediaan_detail': persediaan_detail,
        'ekuitas_detail': ekuitas_detail,
    }

    return render(request, 'ledger/solvabilitas.html', context)
