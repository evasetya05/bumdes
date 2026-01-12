from django.urls import path
from . import views

app_name = 'parkir'

urlpatterns = [
    path('', views.parkir_index, name='index'),
    path('daftar-laporan/', views.report_list, name='report_list'),
    path('<int:pk>/', views.report_detail, name='report_detail'),
    path('<int:pk>/post/', views.post_to_ledger, name='post_to_ledger'),
    path('laporan/harian/tambah/', views.parking_daily_report_create, name='daily_report_create'),
    path('api/ticket-price/', views.get_ticket_price, name='ticket_price'),
]

