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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.modules.ledger.models import Account
        self.fields['revenue_account'].queryset = Account.objects.filter(account_type='INCOME')

    class Meta:
        model = ParkingTicketItem
        fields = ['revenue_account', 'start_serial', 'end_serial', 'lembar', 'price', 'description']


class ParkingExpenseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.modules.ledger.models import Account
        self.fields['expense_account'].queryset = Account.objects.filter(account_type='EXPENSE')

    class Meta:
        model = ParkingExpense
        fields = ['expense_account', 'description', 'percentage', 'unit', 'nominal', 'amount']


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
    extra=1,
    can_delete=True
)
