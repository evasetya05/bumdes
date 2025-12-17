from django.urls import path, include

app_name = 'ledger'  # Add this line to set the app namespace

urlpatterns = [
    path('', include('ledger.urls.index')),
    path('report/', include('ledger.urls.ledger_report')),
    path('report/', include('ledger.urls.profit_loss')),
    path('journal/', include('ledger.urls.journal_entry')),
    path('journal/', include('ledger.urls.journal_edit')),
    path('accounts/', include('ledger.urls.balance_sheet')),
    path('accounts/', include('ledger.urls.account')),
    path('closing/', include('ledger.urls.closing_period')),
    path('solvabilitas/', include('ledger.urls.solvabilitas')),
    path('profitabilitas/', include('ledger.urls.profitabilitas')),
]
