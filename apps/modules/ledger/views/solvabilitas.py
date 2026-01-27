from django.shortcuts import render
from django.db.models import Sum
from apps.modules.ledger.models import Account, JournalItem, ClosingPeriod


def get_balance_by_prefix(prefixes, period=None, year=None):
    """
    Hitung total saldo akun-akun dengan prefix tertentu.
    Bisa filter per periode (YYYY-MM) atau per tahun.
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

        items = JournalItem.objects.filter(account=acc)

        if period:
            items = items.filter(journal_entry__period=period)
        elif year:
            items = items.filter(journal_entry__date__year=year)

        debit = items.aggregate(total=Sum("debit"))["total"] or 0
        credit = items.aggregate(total=Sum("credit"))["total"] or 0

        balance = debit - credit if acc.balance_type == 'Debit' else credit - debit

        total += balance
        detail.append({
            'coa': code,
            'name': acc.account_name,
            'balance': round(balance, 2)
        })

    return total, detail


def solvabilitas_view(request):
    """Laporan Rasio Solvabilitas & Likuiditas (Bulanan / Tahunan)."""

    closed_periods = ClosingPeriod.objects.filter(is_closed=True).order_by('-period')

    mode = request.GET.get("mode", "period")   # period | year
    selected_period = request.GET.get("period")
    selected_year = request.GET.get("year")

    # ===== Default nilai =====
    if mode == "year":
        if not selected_year:
            if closed_periods.exists():
                selected_year = closed_periods.first().period[:4]
    else:
        if not selected_period and closed_periods.exists():
            selected_period = closed_periods.first().period

    if not selected_period and not selected_year:
        return render(request, 'ledger/solvabilitas.html', {'error': 'Belum ada periode yang bisa ditampilkan.'})

    # ===== Ambil saldo =====
    aset_lancar, aset_lancar_detail = get_balance_by_prefix(['1'], selected_period if mode=="period" else None, int(selected_year) if mode=="year" else None)
    kewajiban_lancar, kewajiban_detail = get_balance_by_prefix(['2'], selected_period if mode=="period" else None, int(selected_year) if mode=="year" else None)
    ekuitas, ekuitas_detail = get_balance_by_prefix(['3'], selected_period if mode=="period" else None, int(selected_year) if mode=="year" else None)
    persediaan, persediaan_detail = get_balance_by_prefix(['1200'], selected_period if mode=="period" else None, int(selected_year) if mode=="year" else None)

    total_aset = aset_lancar
    total_kewajiban = kewajiban_lancar
    total_ekuitas = ekuitas

    # ===== Hitung Rasio =====
    rasio_lancar = aset_lancar / total_kewajiban if total_kewajiban else 0
    rasio_cepat = (aset_lancar - persediaan) / total_kewajiban if total_kewajiban else 0
    rasio_utang_aset = total_kewajiban / total_aset if total_aset else 0
    rasio_utang_modal = total_kewajiban / total_ekuitas if total_ekuitas else 0
    rasio_ekuitas_aset = total_ekuitas / total_aset if total_aset else 0

    context = {
        "mode": mode,
        "periods": closed_periods,
        "period": selected_period,
        "year": selected_year,

        # rasio
        "rasio_lancar": round(rasio_lancar, 2),
        "rasio_cepat": round(rasio_cepat, 2),
        "rasio_utang_aset": round(rasio_utang_aset, 2),
        "rasio_utang_modal": round(rasio_utang_modal, 2),
        "rasio_ekuitas_aset": round(rasio_ekuitas_aset, 2),

        # saldo
        "aset_lancar": round(aset_lancar, 2),
        "kewajiban_lancar": round(kewajiban_lancar, 2),
        "persediaan": round(persediaan, 2),
        "ekuitas": round(ekuitas, 2),

        # detail
        "aset_lancar_detail": aset_lancar_detail,
        "kewajiban_detail": kewajiban_detail,
        "persediaan_detail": persediaan_detail,
        "ekuitas_detail": ekuitas_detail,
    }

    return render(request, "ledger/solvabilitas.html", context)
