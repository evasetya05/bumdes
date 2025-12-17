from django.contrib import admin
from django.urls import path, include
from apps.core.views.landing_views import LandingPageView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LandingPageView.as_view(), name='landing-page'),

    # Menyertakan URL dari aplikasi lain
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('users/', include('apps.users.urls', namespace='users')),
    path('ledger/', include('apps.modules.ledger.urls', namespace='ledger')),
    # Anda mungkin perlu menambahkan URL untuk aplikasi lain di sini
    path('', include('apps.core.urls')), # Untuk dashboard, dll.
]