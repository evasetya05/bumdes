from django.urls import include, path
from .views.company_views import (
    UpdateCompanyView,
    DepartmentListView,
    DepartmentCreateView,
    DepartmentUpdateView,
    DepartmentDeleteView,
    PositionListView,
    PositionCreateView,
    PositionUpdateView,
    PositionDeleteView,
)
from .views.index_views import index, pricing, checkout, payment
from .views.user_views import ListUserView, EditUserView, user_profile
from .views.anggota_views import AnggotaListView, AnggotaCreateView, AnggotaUpdateView, PublicAnggotaCreateView, approve_anggota, reject_anggota

app_name = 'anggota'

index_pattern = (
    [
        path('', index, name="index"),
        path('dashboard/', index, name="dashboard"),
        path('pricing/', pricing, name="pricing"),
        path('checkout/', checkout, name="checkout"),
        path('payment/', payment, name="payment"),
    ]
)

company_pattern = (
    [
        path('profile/', UpdateCompanyView.as_view(), name="profile"),
        path('departments/', DepartmentListView.as_view(), name='department'),
        path('departments/add/', DepartmentCreateView.as_view(), name='department_create'),
        path('departments/<int:pk>/edit/', DepartmentUpdateView.as_view(), name='department_update'),
        path('departments/<int:pk>/delete/', DepartmentDeleteView.as_view(), name='department_delete'),
        path('positions/', PositionListView.as_view(), name='position'),
        path('positions/add/', PositionCreateView.as_view(), name='position_create'),
        path('positions/<int:pk>/edit/', PositionUpdateView.as_view(), name='position_update'),
        path('positions/<int:pk>/delete/', PositionDeleteView.as_view(), name='position_delete'),
    ],
    'company'
)

user_pattern = (
    [
        path('list/', ListUserView.as_view(), name="list"),
        path('edit/<int:pk>/', EditUserView.as_view(), name="edit"),
        path('profile/', user_profile, name='user_profile'),
    ],
    'user'
)

anggota_pattern = (
    [
        path('', AnggotaListView.as_view(), name="list"),
        path('tambah/', AnggotaCreateView.as_view(), name="create"),
        path('<int:pk>/edit/', AnggotaUpdateView.as_view(), name="update"),
        path('<int:pk>/approve/', approve_anggota, name="approve"),
        path('<int:pk>/reject/', reject_anggota, name="reject"),
    ]
)

public_pattern = (
    [
        path('pendaftaran/', PublicAnggotaCreateView.as_view(), name="public_create"),
    ]
)

urlpatterns = [
    path('', include(index_pattern)),
    path('', include(public_pattern)),
    path('company/', include(company_pattern)),
    path('user/', include(user_pattern)),
    path('anggota/', include(anggota_pattern)),
]
