import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status

from analytics.models import Domain, PageView
from analytics.tests.factories import DomainFactory, PageViewFactory

TEST_REQUEST_META = {
    "wsgi.url_scheme": "http",
    "PATH_INFO": "/about-me/",
    "REQUEST_URI": "/about-me/",
    "RAW_URI": "/about-me/",
    "REMOTE_ADDR": "127.0.0.1",
    "HTTP_HOST": "localhost:8000",
    "HTTP_USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
    "HTTP_ACCEPT_LANGUAGE": "en-GB,en;q=0.9",
}


class TestAddPageView:
    pytestmark = pytest.mark.django_db
    url = reverse("track_view")

    @pytest.fixture()
    def test_domain(self):
        return DomainFactory.create()

    @staticmethod
    def get_url():
        return reverse("track_view")

    def test__created(self, client, test_domain):
        expected_url = f"{test_domain.base_url}/new-post"
        data = {
            "url": expected_url,
            "domain_id": str(test_domain.id),
            "request_meta": TEST_REQUEST_META,
        }
        response = client.post(self.url, data=data, content_type="application/json")
        assert response.status_code == status.HTTP_201_CREATED
        page_view = PageView.objects.get(domain=test_domain)
        assert page_view.url == expected_url
        assert page_view.ip == "127.0.0.1"
        expected_metadata = {
            "browser": "Safari",
            "os": "Mac OS X",
            "device": "Mac",
            "country": "Unknown",
        }
        assert page_view.metadata == expected_metadata

    def test__passed_url_not_allowed_for_this_domain_id(self, client, test_domain):
        data = {
            "url": f"https://wrong-domain.com/new-post",
            "domain_id": str(test_domain.id),
        }
        response = client.post(self.url, data=data, content_type="application/json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert PageView.objects.filter(domain=test_domain).count() == 0

    def test__domain_id__does_not_exists__error(self, client, test_domain):
        data = {"url": f"{test_domain.base_url}/new-post", "domain_id": "nope"}
        response = client.post(self.url, data=data, content_type="application/json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert PageView.objects.filter(domain=test_domain).count() == 0

    def test__domain_id__not_passed__error(self, client, test_domain):
        data = {
            "url": f"{test_domain.base_url}/new-post",
        }
        response = client.post(self.url, data=data, content_type="application/json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert PageView.objects.filter(domain=test_domain).count() == 0

    def test__request_meta__not_passed__error(self, client, test_domain):
        data = {
            "domain_id": str(test_domain.id),
            "url": f"{test_domain.base_url}/new-post",
        }
        response = client.post(self.url, data=data, content_type="application/json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert PageView.objects.filter(domain=test_domain).count() == 0

    def test__url__not_passed__error(self, client, test_domain):
        data = {"domain_id": str(test_domain.id)}
        response = client.post(self.url, data=data, content_type="application/json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert PageView.objects.filter(domain=test_domain).count() == 0


@pytest.mark.django_db
def test_n_plus_1__chart_page(client, django_assert_max_num_queries):
    PageViewFactory.create_batch(10)
    test_domain = Domain.objects.first()
    superuser = User.objects.create_user(
        username="superuser", password="Qwert1234", is_superuser=True
    )
    client.force_login(superuser)
    with django_assert_max_num_queries(10):
        response = client.get(
            reverse("domain_page_views", kwargs={"pk": test_domain.pk})
        )
        assert response.status_code == status.HTTP_200_OK

    PageViewFactory.create_batch(10)
    with django_assert_max_num_queries(10):
        response = client.get(
            reverse("domain_page_views", kwargs={"pk": test_domain.pk})
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_n_plus_1__home_page(client, django_assert_max_num_queries):
    PageViewFactory.create_batch(1)
    superuser = User.objects.create_user(
        username="superuser", password="Qwert1234", is_superuser=True
    )
    client.force_login(superuser)
    with django_assert_max_num_queries(11):
        response = client.get(reverse("home_view"))
        assert response.status_code == status.HTTP_200_OK

    # todo improve this n+1 effect
    PageViewFactory.create_batch(1)
    with django_assert_max_num_queries(15):
        response = client.get(reverse("home_view"))
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_no_redirect_to_login_page(client):
    response = client.get(reverse("home_view"))
    assert response.status_code == status.HTTP_403_FORBIDDEN
