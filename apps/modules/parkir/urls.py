from django.urls import path
from . import views

app_name = 'parkir'

urlpatterns = [
    path('', views.parkir_index, name='index'),
    path('daftar-laporan/', views.report_list, name='report_list'),
    path('<int:pk>/', views.report_detail, name='report_detail'),
    path('<int:pk>/post/', views.post_to_ledger, name='post_to_ledger'),
    path('<int:pk>/buat-jurnal/', views.report_create_journal, name='report_create_journal'),
    path('laporan/harian/tambah/', views.parking_daily_report_manage, name='daily_report_create'),
    path('laporan/harian/<int:pk>/edit/', views.parking_daily_report_manage, name='daily_report_update'),
    path('api/ticket-price/', views.get_ticket_price, name='ticket_price'),
]

