from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .models import (
    ParkingDailyReport,
    ParkingTicketItem,
    ParkingExpense,
    TicketType,
)
from .services import post_parking_daily_report


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import ParkingDailyReport
from .forms import (
    ParkingDailyReportForm,
    TicketItemFormSet,
    ExpenseFormSet
)

def parkir_index(request):
      return render(request, 'parkir/index.html', {
    })

@require_GET
def get_ticket_price(request):
    """API endpoint untuk mendapatkan harga tiket"""
    ticket_type_id = request.GET.get('ticket_type_id')
    if ticket_type_id:
        try:
            ticket_type = TicketType.objects.get(id=ticket_type_id)
            return JsonResponse({'price': float(ticket_type.price)})
        except TicketType.DoesNotExist:
            return JsonResponse({'error': 'Ticket type not found'}, status=404)
    return JsonResponse({'error': 'Missing ticket_type_id'}, status=400)

@login_required
def parking_daily_report_create(request):
    if request.method == 'POST':
        report_form = ParkingDailyReportForm(request.POST)
        if report_form.is_valid():
            report = report_form.save(commit=False)
            report.created_by = request.user
            report.save()

            ticket_formset = TicketItemFormSet(request.POST, instance=report)
            expense_formset = ExpenseFormSet(request.POST, instance=report)

            if ticket_formset.is_valid() and expense_formset.is_valid():
                ticket_formset.save()
                expense_formset.save()
                return redirect('parkir:report_detail', report.id)
        else:
            ticket_formset = TicketItemFormSet(request.POST)
            expense_formset = ExpenseFormSet(request.POST)
    else:
        report_form = ParkingDailyReportForm()
        ticket_formset = TicketItemFormSet()
        expense_formset = ExpenseFormSet()

    return render(request, 'parkir/daily_report_form.html', {
        'report_form': report_form,
        'ticket_formset': ticket_formset,
        'expense_formset': expense_formset,
    })


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
