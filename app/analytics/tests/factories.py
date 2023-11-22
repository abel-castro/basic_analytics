import random

import factory
from analytics.models import Domain, PageView


class DomainFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Domain

    base_url = factory.Faker("domain_name")


TEST_URI_PATHS = [
    "/my-first-post",
    "/my-second-post",
    "/my-third-post",
]

TEST_BROWSERS = ["Mobile Safari", "Chrome", "UptimeRobot"]

TEST_DEVICES = ["Mac", "iPhone", "Spider"]

TEST_METADATA = {
    "browser": "Mobile Safari",
    "os": "iOS",
    "device": "iPhone",
    "country": "AT",
}


class PageViewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PageView

    domain = factory.SubFactory(DomainFactory)
    ip = factory.Faker("ipv4_public")

    @factory.lazy_attribute
    def url(self):
        uri_path = random.choice(TEST_URI_PATHS)
        return f"{self.domain.base_url}{uri_path}"

    @factory.lazy_attribute
    def metadata(self):
        return TEST_METADATA
