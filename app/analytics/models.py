import uuid

from django.db import models
from django.db.models import Count, F, Func, Value
from django.db.models.functions import TruncMonth
from factory.faker import faker

from analytics.managers import PageViewManager


class Domain(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    base_url = models.URLField()

    def __str__(self):
        return self.base_url

    def get_page_views(self):
        qs = (
            self.page_views.annotate(evaluation_month=TruncMonth("timestamp"))
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

    def get_page_views_by_url(self):
        return (
            self.page_views.values("url")
            .annotate(count=Count("pk", distinct=True))
            .order_by("-count")
        )

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

    def get_browser_analytics(self):
        qs = (
            self.page_views.values("metadata__browser")
            .annotate(browser_count=Count("metadata__browser"))
            .order_by()
        )
        labels = list(qs.values_list("metadata__browser", flat=True))
        colors = self.get_colors(len(labels))
        data = list(qs.values_list("browser_count", flat=True))
        data = self.get_data_in_percentages(data)
        return {"data": data, "colors": colors, "labels": labels}

    def get_country_analytics(self):
        qs = (
            self.page_views.values("metadata__country")
            .annotate(country_count=Count("metadata__country"))
            .order_by()
        )
        labels = list(qs.values_list("metadata__country", flat=True))
        colors = self.get_colors(len(labels))
        data = list(qs.values_list("country_count", flat=True))
        data = self.get_data_in_percentages(data)
        return {"data": data, "colors": colors, "labels": labels}

    def get_device_analytics(self):
        qs = (
            self.page_views.values("metadata__device")
            .annotate(device_count=Count("metadata__device"))
            .order_by()
        )
        labels = list(qs.values_list("metadata__device", flat=True))
        colors = self.get_colors(len(labels))
        data = list(qs.values_list("device_count", flat=True))
        data = self.get_data_in_percentages(data)
        return {"data": data, "colors": colors, "labels": labels}

    def get_os_analytics(self):
        qs = (
            self.page_views.values("metadata__os")
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
