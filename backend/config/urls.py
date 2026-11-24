from django.contrib import admin
from django.urls import path, include
from analyses import page_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("analyses.urls")),
    path("api-auth/", include("rest_framework.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/", include("accounts.urls")),
    path("", page_views.index, name="analysis_home"),
]
