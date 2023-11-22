import pytest
from analytics.helpers import transform_period_string_to_timedelta
from django.utils import timezone


@pytest.mark.parametrize(
    "period, expected_timedelta",
    [
        ("0", None),
        ("all", None),
        ("1", timezone.timedelta(days=30)),
        ("3", timezone.timedelta(days=90)),
        ("6", timezone.timedelta(days=180)),
        ("12", timezone.timedelta(days=365)),
    ],
)
def test_transform_period_string_to_timedelta(period, expected_timedelta):
    assert transform_period_string_to_timedelta(period=period) == expected_timedelta
