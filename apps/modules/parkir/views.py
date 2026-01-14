from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.utils import timezone

from .models import (
    ParkingDailyReport,
    ParkingTicketItem,
    ParkingExpense,
    TicketType,
)
from .services import post_parking_daily_report, prepare_journal_prefill
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
@login_required
def parking_daily_report_manage(request, pk=None):
    if pk:
        report = get_object_or_404(ParkingDailyReport, pk=pk)
        if report.status == 'posted':
            messages.warning(request, "Laporan yang sudah diposting tidak dapat diedit.")
            return redirect('parkir:report_detail', pk=pk)
    else:
        report = None

    ticket_prefix = 'tickets'
    expense_prefix = 'expenses'

    if request.method == 'POST':
        report_form = ParkingDailyReportForm(request.POST, instance=report)
        
        # Handle "Add Ticket" button
        if 'add_ticket' in request.POST:
            cp = request.POST.copy()
            cp[f'{ticket_prefix}-TOTAL_FORMS'] = int(cp.get(f'{ticket_prefix}-TOTAL_FORMS', 0)) + 1
            ticket_formset = TicketItemFormSet(cp, instance=report_form.instance, prefix=ticket_prefix)
            expense_formset = ExpenseFormSet(request.POST, instance=report_form.instance, prefix=expense_prefix)
        
        # Handle "Add Expense" button
        elif 'add_expense' in request.POST:
            cp = request.POST.copy()
            cp[f'{expense_prefix}-TOTAL_FORMS'] = int(cp.get(f'{expense_prefix}-TOTAL_FORMS', 0)) + 1
            ticket_formset = TicketItemFormSet(request.POST, instance=report_form.instance, prefix=ticket_prefix)
            expense_formset = ExpenseFormSet(cp, instance=report_form.instance, prefix=expense_prefix)
            
        # Normal Submission
        else:
            ticket_formset = TicketItemFormSet(request.POST, instance=report_form.instance, prefix=ticket_prefix)
            expense_formset = ExpenseFormSet(request.POST, instance=report_form.instance, prefix=expense_prefix)

            if report_form.is_valid() and ticket_formset.is_valid() and expense_formset.is_valid():
                report_obj = report_form.save(commit=False)
                if not report_obj.pk:
                    report_obj.created_by = request.user
                report_obj.save()
                
                ticket_formset.instance = report_obj
                ticket_formset.save()
                
                expense_formset.instance = report_obj
                expense_formset.save()
                
                return redirect('parkir:report_detail', report_obj.id)
            else:
                messages.error(request, "Terdapat kesalahan. Mohon periksa kembali inputan Anda.")

    else:
        report_form = ParkingDailyReportForm(instance=report)
        ticket_formset = TicketItemFormSet(instance=report, prefix=ticket_prefix)
        expense_formset = ExpenseFormSet(instance=report, prefix=expense_prefix)

    return render(request, 'parkir/daily_report_form.html', {
        'report_form': report_form,
        'ticket_formset': ticket_formset,
        'expense_formset': expense_formset,
        'is_edit': pk is not None
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
        entry = post_parking_daily_report(report.id)
        messages.success(request, 'Berhasil diposting ke Ledger.')
        return redirect('ledger:journal_list')
    except Exception as e:
        messages.error(request, f'Gagal posting: {e}')
        return redirect('parkir:report_detail', pk=pk)


@login_required
def report_create_journal(request, pk):
    report = get_object_or_404(ParkingDailyReport, pk=pk)

    prefill = prepare_journal_prefill(report)
    session_data = {
        'entries': prefill.get('entries', []),
        'description': report.description or f"Laporan Parkir {report.date}",
        'date': report.date.strftime('%Y-%m-%d'),
        'report_id': report.id,
    }

    request.session['journal_prefill'] = session_data

    if prefill.get('cash_warning'):
        messages.warning(request, prefill['cash_warning'])

    messages.info(request, 'Silakan periksa draft jurnal dan simpan untuk menyelesaikan posting.')

    return redirect('ledger:create_journal_entry')
