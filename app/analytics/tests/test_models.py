import pytest
from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from analytics.models import Domain
from analytics.tests.factories import DomainFactory, PageViewFactory


class TestAnalytics(TestCase):
    pytestmark = pytest.mark.django_db

    def setUp(self) -> None:
        call_command("create_test_data")
        self.test_domain = Domain.objects.first()

    def test__domain_get_page_views(self):
        expected_data = [
            2,
            4,
            6,
            8,
            10,
            12,
            14,
            16,
            18,
            20,
            22,
            24,
        ] * 2
        expected_months = [
            "2020-01",
            "2020-02",
            "2020-03",
            "2020-04",
            "2020-05",
            "2020-06",
            "2020-07",
            "2020-08",
            "2020-09",
            "2020-10",
            "2020-11",
            "2020-12",
            "2021-01",
            "2021-02",
            "2021-03",
            "2021-04",
            "2021-05",
            "2021-06",
            "2021-07",
            "2021-08",
            "2021-09",
            "2021-10",
            "2021-11",
            "2021-12",
        ]
        page_views = self.test_domain.get_page_views_data()

        assert expected_months == page_views["months"]
        assert expected_data == page_views["data"]

    def test__domain_country_analytics(self):
        expected_countries = ["AT"]
        expected_data = [100]
        country_analytics = self.test_domain.get_country_analytics()

        assert country_analytics["colors"]
        assert expected_countries == country_analytics["labels"]
        assert expected_data == country_analytics["data"]

    def test__domain_browser_analytics(self):
        expected_countries = ["Mobile Safari"]
        expected_data = [100]
        browser_analytics = self.test_domain.get_browser_analytics()

        assert browser_analytics["colors"]
        assert expected_countries == browser_analytics["labels"]
        assert expected_data == browser_analytics["data"]

    def test__domain_os_analytics(self):
        expected_countries = ["iOS"]
        expected_data = [100]
        os_analytics = self.test_domain.get_os_analytics()

        assert os_analytics["colors"]
        assert expected_countries == os_analytics["labels"]
        assert expected_data == os_analytics["data"]

    def test__domain_device_analytics(self):
        expected_countries = ["iPhone"]
        expected_data = [100]
        device_analytics = self.test_domain.get_device_analytics()

        assert device_analytics["colors"]
        assert expected_countries == device_analytics["labels"]
        assert expected_data == device_analytics["data"]

    def test__get_monthly_average_views(self):
        assert self.test_domain.get_monthly_average_page_views() == 13


class TestNoRobotsAnalytics:
    pytestmark = pytest.mark.django_db

    @pytest.mark.parametrize("browser", ["AhrefsBot", "UptimeRobot", "Imaginary bot"])
    def test__get_page_views__no_robots__browsers(self, browser):
        domain = DomainFactory.create()
        robot_metadata = {
            "browser": browser,
            "os": "Other",
            "device": "Other",
            "country": "Unknown",
        }
        PageViewFactory.create_batch(10, domain=domain, metadata=robot_metadata)
        PageViewFactory.create_batch(10, domain=domain)
        assert domain.get_page_views_data(no_robots=True)["data"] == [10]

    @pytest.mark.parametrize("device", settings.EXCLUDED_DEVICES)
    def test__get_page_views__no_robots__devices(self, device):
        domain = DomainFactory.create()
        robot_metadata = {
            "browser": "Other",
            "os": "Other",
            "device": device,
            "country": "Unknown",
        }
        PageViewFactory.create_batch(10, domain=domain, metadata=robot_metadata)
        PageViewFactory.create_batch(10, domain=domain)
        assert domain.get_page_views_data(no_robots=True)["data"] == [10]


@pytest.mark.django_db
def test_get_monthly_average_views():
    domain = DomainFactory.create()
    robot_metadata = {
        "browser": "Other",
        "os": "Other",
        "device": settings.EXCLUDED_DEVICES[0],
        "country": "Unknown",
    }
    PageViewFactory.create_batch(20, domain=domain, metadata=robot_metadata)
    PageViewFactory.create_batch(10, domain=domain)
    assert domain.get_monthly_average_page_views() == 30
    assert domain.get_monthly_average_page_views(no_robots=True) == 10


@pytest.mark.django_db
def test__domain_manager__get_monthly_average_page_views():
    domain = DomainFactory.create()
    PageViewFactory.create_batch(10, domain=domain)
    expected_data = [
        {
            "domain": domain.base_url,
            "with_robots": 10,
            "no_robots": 10,
        }
    ]
    assert Domain.objects.get_monthly_average_page_views() == expected_data
