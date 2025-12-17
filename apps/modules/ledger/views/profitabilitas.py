from django.shortcuts import render
from django.db.models import Sum
from ledger.models.account import Account
from ledger.models.journal_entry import JournalItem
from ledger.models.closing_period import ClosingPeriod


def profitabilitas_view(request):
    all_periods = ClosingPeriod.objects.all().order_by('-period')
    period = request.GET.get("period")
    if not period:
        closed_period = ClosingPeriod.objects.filter(is_closed=True).order_by('-period').first()
        period = closed_period.period if closed_period else ClosingPeriod.get_open_period().period

    def raw_account_saldos(akun_queryset):
        """
        Kembalikan list of dict per akun: {'nama','saldo'} dengan sign sesuai account_type.
        """
        rows = []
        for akun in akun_queryset.order_by("account_name"):
            items = JournalItem.objects.filter(journal_entry__period=period, account=akun)
            debit = items.aggregate(Sum("debit"))["debit__sum"] or 0
            credit = items.aggregate(Sum("credit"))["credit__sum"] or 0
            if akun.account_type in ["ASSET", "EXPENSES", "COGS"]:
                saldo_akhir = float(debit - credit)
            else:
                saldo_akhir = float(credit - debit)
            # Sertakan akun meskipun saldo 0, tapi bisa disaring di template bila perlu
            rows.append({"nama": akun.account_name, "saldo": saldo_akhir})
        return rows

    def total_from_rows(rows):
        return sum(r["saldo"] for r in rows)

    # Ambil akun
    akun_aset = Account.objects.filter(account_type="ASSET")
    akun_modal = Account.objects.filter(account_type="CAPITAL")
    akun_pendapatan = Account.objects.filter(account_type="INCOME")
    akun_hpp = Account.objects.filter(account_type="COGS")
    akun_biaya = Account.objects.filter(account_type="EXPENSES")

    # Hitung rows & totals per kelompok
    pendapatan_rows = raw_account_saldos(akun_pendapatan)
    biaya_rows = raw_account_saldos(akun_biaya)
    hpp_rows = raw_account_saldos(akun_hpp)
    aset_rows = raw_account_saldos(akun_aset)
    modal_rows = raw_account_saldos(akun_modal)

    total_pendapatan = total_from_rows(pendapatan_rows)
    total_hpp = total_from_rows(hpp_rows)
    total_biaya = total_from_rows(biaya_rows)
    total_aset = total_from_rows(aset_rows)
    total_modal = total_from_rows(modal_rows)

    laba_kotor = total_pendapatan - total_hpp
    laba_bersih = laba_kotor - total_biaya

    fmt = lambda n: f"{n:,.2f}"

    ratios = []

    def add_ratio_profitabilitas(nama, rumus, numerator_value, denominator_value,
                                 numerator_detail, denominator_detail):
        """
        numerator_detail dan denominator_detail adalah dicts/rows yg dipakai untuk show:
        numerator_detail bisa berupa dict {'pendapatan_rows':..., 'total_pendapatan':..., 'biaya_rows':..., 'total_biaya':..., 'net':...}
        denominator_detail adalah rows list + total
        """
        hasil = numerator_value / denominator_value if denominator_value else 0
        ratios.append({
            "nama": nama,
            "rumus": rumus,
            "detail": f"➡️ {fmt(numerator_value)} / {fmt(denominator_value)} = {hasil:.2f}",
            "hasil": hasil,
            "numerator": numerator_detail,
            "denominator": denominator_detail,
        })

    # Siapkan numerator_detail structure: pendapatan + biaya + net
    pendapatan_detail = {"rows": pendapatan_rows, "total": total_pendapatan}
    biaya_detail = {"rows": biaya_rows, "total": total_biaya}
    numerator_for_profit = {
        "pendapatan": pendapatan_detail,
        "biaya": biaya_detail,
        "laba_kotor": {"value": laba_kotor},
        "laba_bersih": {"value": laba_bersih},
    }

    # denominator details
    aset_detail = {"rows": aset_rows, "total": total_aset}
    modal_detail = {"rows": modal_rows, "total": total_modal}

    # Tambahkan rasio profitabilitas
    add_ratio_profitabilitas(
        "Return on Assets (ROA)",
        "Laba Bersih / Total Aset",
        laba_bersih, total_aset,
        numerator_for_profit, aset_detail
    )

    add_ratio_profitabilitas(
        "Return on Equity (ROE)",
        "Laba Bersih / Total Modal",
        laba_bersih, total_modal,
        numerator_for_profit, modal_detail
    )

    add_ratio_profitabilitas(
        "Net Profit Margin (NPM)",
        "Laba Bersih / Pendapatan",
        laba_bersih, total_pendapatan,
        numerator_for_profit, pendapatan_detail
    )

    add_ratio_profitabilitas(
        "Gross Profit Margin (GPM)",
        "Laba Kotor / Pendapatan",
        laba_kotor, total_pendapatan,
        {"pendapatan": pendapatan_detail, "hpp": {"rows": hpp_rows, "total": total_hpp}, "laba_kotor": {"value": laba_kotor}}, pendapatan_detail
    )

    context = {
        "periode": period,
        "periods": all_periods,
        "pendapatan": total_pendapatan,
        "hpp": total_hpp,
        "biaya": total_biaya,
        "laba_kotor": laba_kotor,
        "laba_bersih": laba_bersih,
        "ratios": ratios,
    }

    return render(request, "ledger/profitabilitas.html", context)
