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
from django.views.decorators.cache import cache_page

from analytics.views import (DomainBrowserAnalytics, DomainCountryAnalytics,
                             DomainDeviceAnalytics, DomainOSAnalytics,
                             DomainPageViews, DomainPageViewsByUrl, HomeView,
                             TrackView)

urlpatterns = [
    path(f"{settings.ADMIN_URL}/", admin.site.urls),
    path("", cache_page(60 * 60)(HomeView.as_view()), name="home_view"),
    path(
        "domain/<pk>/page-views",
        cache_page(60 * 60)(DomainPageViews.as_view()),
        name="domain_page_views",
    ),
    path(
        "domain/<pk>/page-views-by-url",
        cache_page(60 * 60)(DomainPageViewsByUrl.as_view()),
        name="domain_page_views_by_url",
    ),
    path(
        "domain/<pk>/browser-analytics",
        cache_page(60 * 60)(DomainBrowserAnalytics.as_view()),
        name="domain_browser_analytics",
    ),
    path(
        "domain/<pk>/country-analytics",
        cache_page(60 * 60)(DomainCountryAnalytics.as_view()),
        name="domain_country_analytics",
    ),
    path(
        "domain/<pk>/device-analytics",
        cache_page(60 * 60)(DomainDeviceAnalytics.as_view()),
        name="domain_device_analytics",
    ),
    path(
        "domain/<pk>/os-analytics",
        cache_page(60 * 60)(DomainOSAnalytics.as_view()),
        name="domain_os_analytics",
    ),
    path("api/track/", TrackView.as_view(), name="track_view"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
