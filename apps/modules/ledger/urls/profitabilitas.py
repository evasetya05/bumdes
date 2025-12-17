from django.urls import path
from ledger.views.profitabilitas import profitabilitas_view

urlpatterns = [
    path('profitabilitas/', profitabilitas_view, name='profitabilitas'),
]
