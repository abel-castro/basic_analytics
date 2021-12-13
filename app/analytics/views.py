from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView
from django.views.generic.base import ContextMixin
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from analytics.managers import PageViewCreationError
from analytics.models import Domain, PageView


class DashboardPageMixin(LoginRequiredMixin, ContextMixin):
    page_title = ""

    def get_page_title(self) -> str:
        return f"{self.page_title} for {self.get_object()}"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.get_page_title()
        context["domains"] = Domain.objects.only("id", "base_url")
        return context


class PieAnalyticsMixin(DashboardPageMixin, DetailView):
    template_name = "pie_analytics.html"
    model = Domain
    get_data_function = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        analytics = getattr(self.get_object(), self.get_data_function)()
        context["colors"] = analytics["colors"]
        context["labels"] = analytics["labels"]
        context["data"] = analytics["data"]
        return context


class HomeView(DashboardPageMixin, ListView):
    template_name = "home.html"
    model = Domain

    def get_page_title(self) -> str:
        return "Dashboard"


class DomainPageViews(DashboardPageMixin, DetailView):
    template_name = "domain_page_views.html"
    model = Domain
    page_title = "Page views"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_views = self.get_object().get_page_views()
        context["data"] = page_views["data"]
        context["months"] = page_views["months"]
        return context


class DomainPageViewsByUrl(DashboardPageMixin, DetailView):
    template_name = "domain_page_views_by_url.html"
    model = Domain
    page_title = "Page views by url"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_views_by_url = self.get_object().get_page_views_by_url()
        context["data"] = page_views_by_url
        return context


class DomainBrowserAnalytics(PieAnalyticsMixin):
    page_title = "Browser analytics"
    get_data_function = "get_browser_analytics"


class DomainCountryAnalytics(PieAnalyticsMixin):
    page_title = "Country analytics"
    get_data_function = "get_country_analytics"


class DomainDeviceAnalytics(PieAnalyticsMixin):
    page_title = "Device analytics"
    get_data_function = "get_device_analytics"


class DomainOSAnalytics(PieAnalyticsMixin):
    page_title = "OS analytics"
    get_data_function = "get_os_analytics"


class TrackView(APIView):
    allowed_methods = ["POST"]

    def post(self, request, *args, **kwargs):
        status_code = status.HTTP_201_CREATED
        payload = {}
        try:
            PageView.objects.create_from_request(request=request)
            payload["message"] = "PageView created"
        except PageViewCreationError as e:
            status_code = status.HTTP_400_BAD_REQUEST
            payload["message"] = f"Error: {e}"
        return Response(status=status_code, data=payload)
