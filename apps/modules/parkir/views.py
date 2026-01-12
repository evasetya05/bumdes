from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum

from .models import (
    ParkingDailyReport,
    ParkingTicketItem,
    ParkingExpense,
)
from .services import post_parking_daily_report

@login_required
def report_list(request):
    reports = ParkingDailyReport.objects.all().order_by('-date')
    return render(request, 'parkir/report_list.html', {
        'reports': reports
    })


@login_required
def report_detail(request, pk):
    report = get_object_or_404(ParkingDailyReport, pk=pk)

    tickets = report.items.all()
    expenses = report.expenses.all()

    total_bruto = report.total_bruto()
    total_expense = expenses.aggregate(
        total=Sum('amount')
    )['total'] or 0

    context = {
        'report': report,
        'tickets': tickets,
        'expenses': expenses,
        'total_bruto': total_bruto,
        'total_expense': total_expense,
        'net_cash': total_bruto - total_expense,
    }
    return render(request, 'parkir/report_detail.html', context)


@login_required
def post_to_ledger(request, pk):
    report = get_object_or_404(ParkingDailyReport, pk=pk)

    if report.status == 'posted':
        messages.warning(request, 'Laporan ini sudah diposting.')
        return redirect('parkir:report_detail', pk=pk)

    try:
        post_parking_daily_report(report.id)
        messages.success(request, 'Berhasil diposting ke Ledger.')
    except Exception as e:
        messages.error(request, f'Gagal posting: {e}')

    return redirect('parkir:report_detail', pk=pk)
