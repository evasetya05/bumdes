# ratios/urls.py
from django.urls import path
from apps.modules.ledger.views.solvabilitas import solvabilitas_view

urlpatterns = [
    path('solvabilitas/', solvabilitas_view, name='solvabilitas'),
]
