import uuid
from typing import Optional

from analytics.helpers import transform_period_string_to_timedelta
from analytics.managers import DomainManager, PageViewManager
from django.conf import settings
from django.db import models
from django.db.models import Count, F, Func, QuerySet, Value
from django.db.models.functions import TruncMonth
from django.utils import timezone
from factory.faker import faker


class Domain(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    base_url = models.URLField()

    objects = DomainManager()

    def __str__(self):
        return self.base_url

    @staticmethod
    def get_data_in_percentages(data: list) -> list:
        total = sum(data)
        new_data = []
        for element in data:
            new_data.append(round(element * 100 / total, 2))
        return new_data

    @staticmethod
    def get_colors(amount_colors) -> list:
        colors = []
        fake = faker.Faker()
        for i in range(amount_colors):
            colors.append(fake.hex_color())

        return colors

    def get_page_views(
        self, period_timedelta: Optional[timezone.timedelta], with_robots: bool = False
    ) -> QuerySet:
        page_views = self.page_views

        if not with_robots:
            page_views = page_views.exclude(
                metadata__device__in=settings.EXCLUDED_DEVICES
            ).exclude(metadata__browser__icontains="bot")

        if period_timedelta:
            now = timezone.now()
            start_date = now - period_timedelta
            page_views = page_views.filter(timestamp__range=(start_date, now))
        return page_views

    def get_monthly_average_page_views(self, with_robots: bool = False) -> float:
        page_views = self.get_page_views_data(with_robots=with_robots)["data"]
        try:
            value = round(sum(page_views) / len(page_views), 2)
        except ZeroDivisionError:
            value = 0
        return value

    def get_page_views_data(
        self, period: str = "all", with_robots: bool = False
    ) -> dict:
        period_timedelta = transform_period_string_to_timedelta(period=period)
        page_views = self.get_page_views(
            period_timedelta=period_timedelta, with_robots=with_robots
        )
        qs = (
            page_views.annotate(evaluation_month=TruncMonth("timestamp"))
            .values("evaluation_month")
            .annotate(Count("pk", distinct=True))
        ).order_by("evaluation_month")
        qs = qs.annotate(
            iso_evaluation_month=Func(
                F("evaluation_month"),
                Value("YYYY-MM"),
                function="to_char",
                output_field=models.CharField(),
            )
        )
        months = list(qs.values_list("iso_evaluation_month", flat=True))
        data = list(qs.values_list("pk__count", flat=True))
        return {"data": data, "months": months}

    def get_page_views_by_url(
        self, period: str = "all", with_robots: bool = False
    ) -> QuerySet:
        period_timedelta = transform_period_string_to_timedelta(period=period)
        page_views = self.get_page_views(
            period_timedelta=period_timedelta, with_robots=with_robots
        )

        return (
            page_views.values("url")
            .annotate(count=Count("pk", distinct=True))
            .order_by("-count")
        )

    def get_browser_analytics(
        self, period: str = "all", with_robots: bool = False
    ) -> dict:
        period_timedelta = transform_period_string_to_timedelta(period=period)
        page_views = self.get_page_views(
            period_timedelta=period_timedelta, with_robots=with_robots
        )

        qs = (
            page_views.values("metadata__browser")
            .annotate(browser_count=Count("metadata__browser"))
            .order_by()
        )
        labels = list(qs.values_list("metadata__browser", flat=True))
        colors = self.get_colors(len(labels))
        data = list(qs.values_list("browser_count", flat=True))
        data = self.get_data_in_percentages(data)
        return {"data": data, "colors": colors, "labels": labels}

    def get_country_analytics(
        self, period: str = "all", with_robots: bool = False
    ) -> dict:
        period_timedelta = transform_period_string_to_timedelta(period=period)
        page_views = self.get_page_views(
            period_timedelta=period_timedelta, with_robots=with_robots
        )
        qs = (
            page_views.values("metadata__country")
            .annotate(country_count=Count("metadata__country"))
            .order_by()
        )
        labels = list(qs.values_list("metadata__country", flat=True))
        colors = self.get_colors(len(labels))
        data = list(qs.values_list("country_count", flat=True))
        data = self.get_data_in_percentages(data)
        return {"data": data, "colors": colors, "labels": labels}

    def get_device_analytics(
        self, period: str = "all", with_robots: bool = False
    ) -> dict:
        period_timedelta = transform_period_string_to_timedelta(period=period)
        page_views = self.get_page_views(
            period_timedelta=period_timedelta, with_robots=with_robots
        )
        qs = (
            page_views.values("metadata__device")
            .annotate(device_count=Count("metadata__device"))
            .order_by()
        )
        labels = list(qs.values_list("metadata__device", flat=True))
        colors = self.get_colors(len(labels))
        data = list(qs.values_list("device_count", flat=True))
        data = self.get_data_in_percentages(data)
        return {"data": data, "colors": colors, "labels": labels}

    def get_os_analytics(self, period: str = "all", with_robots: bool = False) -> dict:
        period_timedelta = transform_period_string_to_timedelta(period=period)
        page_views = self.get_page_views(
            period_timedelta=period_timedelta, with_robots=with_robots
        )
        qs = (
            page_views.values("metadata__os")
            .annotate(os_count=Count("metadata__os"))
            .order_by()
        )
        labels = list(qs.values_list("metadata__os", flat=True))
        colors = self.get_colors(len(labels))
        data = list(qs.values_list("os_count", flat=True))
        data = self.get_data_in_percentages(data)
        return {"data": data, "colors": colors, "labels": labels}


class PageView(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    domain = models.ForeignKey(
        Domain, related_name="page_views", on_delete=models.CASCADE
    )
    ip = models.GenericIPAddressField()
    metadata = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)
    url = models.URLField()

    objects = PageViewManager()

    def __str__(self):
        return f"{self.url} view at {self.timestamp}"
