from typing import Any
from urllib.parse import unquote

import settings
from analytics.managers import PageViewCreationError
from analytics.models import Domain, PageView
from django.contrib.auth import logout
from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.views.generic import DetailView, ListView, RedirectView
from django.views.generic.base import ContextMixin
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class CustomLoginRequiredMixin(AccessMixin):
    """
    django.contrib.auth.mixins.LoginRequiredMixin redirects to the login page but as we
    want to hide the login url we return an 403 instead.
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class DashboardPageMixin(CustomLoginRequiredMixin, ContextMixin):
    page_title = ""

    def get_with_robots_value(self) -> bool:
        """
        Return if robots data should be displayed or not.

        This will be defined by passing the query parameter '?with_robots=true'
        Only if '?with_robots=true' no robot data will be returned.
        """
        return self.request.GET.get("with_robots") in ["true", "True"]

    def get_page_title(self) -> str:
        return f"{self.page_title} for {self.get_object()}"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.period = self.request.GET.get("period")
        context["page_title"] = self.get_page_title()
        context["is_robots_page"] = self.get_with_robots_value()
        context["domains"] = Domain.objects.only("id", "base_url")
        context["django_admin_url"] = settings.ADMIN_URL
        return context


class PieAnalyticsMixin(DashboardPageMixin, DetailView):
    template_name = "pie_analytics.html"
    model = Domain
    get_data_function = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        analytics = getattr(self.get_object(), self.get_data_function)(
            with_robots=self.get_with_robots_value()
        )
        context["colors"] = analytics["colors"]
        context["labels"] = analytics["labels"]
        context["data"] = analytics["data"]
        return context


class LogoutView(RedirectView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)
        return super().dispatch(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return settings.LOGIN_URL


class HomeView(DashboardPageMixin, ListView):
    template_name = "home.html"
    model = Domain

    def get_with_robots_value(self) -> bool:
        return False

    def get_page_title(self) -> str:
        return "Dashboard"


class DomainPageViews(DashboardPageMixin, DetailView):
    template_name = "domain_page_views.html"
    model = Domain
    page_title = "Page views"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_views = self.get_object().get_page_views_data(
            period=self.period, with_robots=self.get_with_robots_value()
        )
        context[
            "average_views_with_robots"
        ] = self.get_object().get_monthly_average_page_views(with_robots=True)
        context[
            "average_views_no_robots"
        ] = self.get_object().get_monthly_average_page_views(with_robots=False)
        context["data"] = page_views["data"]
        context["months"] = page_views["months"]
        return context


class DomainPageViewsByUrl(DashboardPageMixin, DetailView):
    template_name = "domain_page_views_by_url.html"
    model = Domain
    page_title = "Page views by url"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_views_by_url = self.get_object().get_page_views_by_url(
            period=self.period, with_robots=self.get_with_robots_value()
        )
        context["pk"] = self.kwargs.get("pk")
        context["data"] = page_views_by_url
        return context


class DomainPageViewsByUrlElement(DashboardPageMixin, ListView):
    template_name = "domain_page_views_by_url_element.html"
    model = PageView

    def get_queryset(self):
        pk = self.kwargs.get("pk")
        url = unquote(self.kwargs.get("url"))
        return self.model.objects.filter(domain__pk=pk, url=url).order_by("timestamp")

    def get_page_title(self) -> str:
        return f"Page views for the url '{self.kwargs.get('url')}'"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        domain_pk = self.kwargs.get("pk")
        url = unquote(self.kwargs.get("url"))

        page_views = PageView.objects.get_views_for_url(
            domain_pk=domain_pk, url=url, with_robots=self.get_with_robots_value()
        )
        context["data"] = page_views["data"]
        context["months"] = page_views["months"]
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
