from django.urls import path
from apps.modules.ledger.views.index import index
from apps.modules.ledger.views.ledger_report import ledger_report

urlpatterns = [
    path('', index, name='ledger_index'),  # / --> halaman utama
]
