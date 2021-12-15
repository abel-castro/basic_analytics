from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied
from django.views.generic import DetailView, ListView
from django.views.generic.base import ContextMixin
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from analytics.managers import PageViewCreationError
from analytics.models import Domain, PageView


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

    def get_no_robots_value(self) -> bool:
        """
        Return if robots data should be displayed or not.

        This will be defined by passing the query parameter '?no_robots=true'
        Only if '?no_robots=true' no robot data will be returned.
        """
        return self.request.GET.get("no_robots") == "true"

    def get_page_title(self) -> str:
        return f"{self.page_title} for {self.get_object()}"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.get_page_title()
        context["is_robots_page"] = not self.get_no_robots_value()
        context["domains"] = Domain.objects.only("id", "base_url")
        return context


class PieAnalyticsMixin(DashboardPageMixin, DetailView):
    template_name = "pie_analytics.html"
    model = Domain
    get_data_function = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        analytics = getattr(self.get_object(), self.get_data_function)(
            self.get_no_robots_value()
        )
        context["colors"] = analytics["colors"]
        context["labels"] = analytics["labels"]
        context["data"] = analytics["data"]
        return context


class HomeView(DashboardPageMixin, ListView):
    template_name = "home.html"
    model = Domain

    def get_no_robots_value(self) -> bool:
        return True

    def get_page_title(self) -> str:
        return "Dashboard"


class DomainPageViews(DashboardPageMixin, DetailView):
    template_name = "domain_page_views.html"
    model = Domain
    page_title = "Page views"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_views = self.get_object().get_page_views_data(self.get_no_robots_value())
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
            self.get_no_robots_value()
        )
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
