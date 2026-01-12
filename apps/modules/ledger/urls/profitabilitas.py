from django.urls import path
from apps.modules.ledger.views.profitabilitas import profitabilitas_view

urlpatterns = [
    path('profitabilitas/', profitabilitas_view, name='profitabilitas'),
]
