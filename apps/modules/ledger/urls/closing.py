# ledger/urls.py
from django.urls import path

from ledger import views
from ledger.views.closing_period import closing_list, closing_create  # ✅ ini memanggil fungsi dari file journal_edit.py

urlpatterns = [
    path('closing/', views.closing_list, name='closing_list'),
    path('closing/new/', views.closing_create, name='closing_create'),
]
