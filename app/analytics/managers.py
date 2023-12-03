import json
from typing import Dict

from analytics.helpers import (get_client_ip_from_request_meta,
                               get_page_view_metadata_from_request_meta)
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Count, F, Func, Value
from django.db.models.functions import TruncDay
from rest_framework.request import Request


class PageViewCreationError(Exception):
    """
    Exception class for PageView creation errors.
    """


class DomainManager(models.Manager):
    def get_monthly_average_page_views(self) -> list:
        monthly_average_page_views = []
        for domain in self.model.objects.all().prefetch_related("page_views"):
            data = {
                "domain": domain.base_url,
                "with_robots": domain.get_monthly_average_page_views(with_robots=True),
                "no_robots": domain.get_monthly_average_page_views(with_robots=False),
            }
            monthly_average_page_views.append(data)
        return monthly_average_page_views


class PageViewManager(models.Manager):
    def get_views_for_url(self, domain_pk: str, url: str, with_robots: bool) -> Dict:
        page_views = self.model.objects.filter(domain__pk=domain_pk, url=url)
        qs = (
            page_views.annotate(day_with_views=TruncDay("timestamp"))
            .values("day_with_views")
            .annotate(Count("pk", distinct=True))
        ).order_by("day_with_views")
        qs = qs.annotate(
            day_with_views_iso_format=Func(
                F("day_with_views"),
                Value("YYYY-MM-DD"),
                function="to_char",
                output_field=models.CharField(),
            )
        )
        days = list(qs.values_list("day_with_views_iso_format", flat=True))
        data = list(qs.values_list("pk__count", flat=True))
        return {"data": data, "days": days}

    def create_from_request(self, request: Request):
        from analytics.models import Domain

        domain_id = request.data.get("domain_id")
        try:
            domain = Domain.objects.get(id=domain_id)
        except ValidationError:
            raise PageViewCreationError(
                f"PageView could not be created because the domain_id {domain_id} is not valid."
            )
        except Domain.DoesNotExist:
            raise PageViewCreationError(
                f"PageView could not be created because a domain with the id "
                f"{domain_id} does not exists."
            )

        try:
            page_view_url = request.data["url"]
        except KeyError:
            raise PageViewCreationError(
                "PageView could not be created because no valid url was passed"
            )

        if domain.base_url not in page_view_url:
            raise PageViewCreationError(
                f"PageView could not be created the request url does not belong to the domain with domain_id {domain_id}"
            )
        try:
            request_meta = request.data["request_meta"]
        except KeyError:
            raise PageViewCreationError(
                "PageView could not be created because no valid request meta was passed"
            )
        if domain_id and page_view_url and request_meta:
            return self.create(
                domain=domain,
                url=page_view_url,
                ip=get_client_ip_from_request_meta(request_meta),
                metadata=get_page_view_metadata_from_request_meta(request_meta),
            )
        raise PageViewCreationError(
            f"PageView could not be created because an required parameter is missing"
        )
