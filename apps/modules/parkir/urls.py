from django.urls import path
from . import views

app_name = 'parkir'

urlpatterns = [
    path('', views.report_list, name='report_list'),
    path('<int:pk>/', views.report_detail, name='report_detail'),
    path('<int:pk>/post/', views.post_to_ledger, name='post_to_ledger'),
]
