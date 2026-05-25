from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.views.decorators.csrf import ensure_csrf_cookie

schema_view = get_schema_view(
    openapi.Info(
        title="AIEngineer Auth API",
        default_version='v1',
        description="Authentication API with cookie-based auth",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # This points to the app below!
    path('api/', include('authentication.urls')),
    path('swagger/', ensure_csrf_cookie(schema_view.with_ui('swagger', cache_timeout=0)), name='swagger'),
    path('', ensure_csrf_cookie(TemplateView.as_view(template_name='index.html')), name='home'),
]