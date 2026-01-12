from django import forms
from django.forms import inlineformset_factory
from .models import (
    ParkingDailyReport,
    ParkingTicketItem,
    ParkingExpense
)

class ParkingDailyReportForm(forms.ModelForm):
    class Meta:
        model = ParkingDailyReport
        fields = ['date', 'description']


class ParkingTicketItemForm(forms.ModelForm):
    class Meta:
        model = ParkingTicketItem
        fields = ['ticket_type', 'start_serial', 'end_serial', 'lembar', 'description']


class ParkingExpenseForm(forms.ModelForm):
    class Meta:
        model = ParkingExpense
        fields = ['description', 'amount']


TicketItemFormSet = inlineformset_factory(
    ParkingDailyReport,
    ParkingTicketItem,
    form=ParkingTicketItemForm,
    extra=1,
    can_delete=True
)

ExpenseFormSet = inlineformset_factory(
    ParkingDailyReport,
    ParkingExpense,
    form=ParkingExpenseForm,
    extra=2,
    can_delete=True
)
