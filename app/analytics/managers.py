from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from rest_framework.request import Request

from analytics.helpers import (get_client_ip_from_request_meta,
                               get_page_view_metadata_from_request_meta)


class PageViewCreationError(Exception):
    """
    Exception class for PageView creation errors.
    """


class PageViewManager(models.Manager):
    def without_robots(self):
        """
        Exclude robot generated page views from the queryset.
        """
        return (
            self.get_queryset()
            .exclude(metadata__device__in=settings.ROBOT_DEVICES)
            .exclude(metadata__browser__in=settings.ROBOT_BROWSERS)
        )

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
