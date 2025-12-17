from django.urls import path
from ledger.views import closing_period

urlpatterns = [
    path('closing-periods/', closing_period.closing_period_list, name='closing_period_list'),
   
    path('closing-periods/<str:period>/close/', closing_period.close_period, name='close_period'),
   
]