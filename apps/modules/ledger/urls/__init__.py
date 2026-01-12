from django.urls import path, include

app_name = 'ledger'  # Add this line to set the app namespace

urlpatterns = [
    path('', include('apps.modules.ledger.urls.index')),
    path('report/', include('apps.modules.ledger.urls.ledger_report')),
    path('report/', include('apps.modules.ledger.urls.profit_loss')),
    path('journal/', include('apps.modules.ledger.urls.journal_entry')),
    path('journal/', include('apps.modules.ledger.urls.journal_edit')),
    path('accounts/', include('apps.modules.ledger.urls.balance_sheet')),
    path('accounts/', include('apps.modules.ledger.urls.account')),
    path('closing/', include('apps.modules.ledger.urls.closing_period')),
    path('solvabilitas/', include('apps.modules.ledger.urls.solvabilitas')),
    path('profitabilitas/', include('apps.modules.ledger.urls.profitabilitas')),
]
