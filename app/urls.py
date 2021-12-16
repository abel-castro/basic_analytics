"""basic_analytics URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from analytics.views import (
    DomainBrowserAnalytics,
    DomainCountryAnalytics,
    DomainDeviceAnalytics,
    DomainOSAnalytics,
    DomainPageViews,
    DomainPageViewsByUrl,
    HomeView,
    LogoutView,
    TrackView,
)

urlpatterns = [
    path(f"{settings.ADMIN_URL}/", admin.site.urls),
    path("", HomeView.as_view(), name="home_view"),
    path("logout/", LogoutView.as_view(), name="logout_view"),
    path(
        "domain/<pk>/page-views",
        DomainPageViews.as_view(),
        name="domain_page_views",
    ),
    path(
        "domain/<pk>/page-views-by-url",
        DomainPageViewsByUrl.as_view(),
        name="domain_page_views_by_url",
    ),
    path(
        "domain/<pk>/browser-analytics",
        DomainBrowserAnalytics.as_view(),
        name="domain_browser_analytics",
    ),
    path(
        "domain/<pk>/country-analytics",
        DomainCountryAnalytics.as_view(),
        name="domain_country_analytics",
    ),
    path(
        "domain/<pk>/device-analytics",
        DomainDeviceAnalytics.as_view(),
        name="domain_device_analytics",
    ),
    path(
        "domain/<pk>/os-analytics",
        DomainOSAnalytics.as_view(),
        name="domain_os_analytics",
    ),
    path("api/track/", TrackView.as_view(), name="track_view"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
