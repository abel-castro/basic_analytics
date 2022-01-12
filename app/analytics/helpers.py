from django.contrib.gis.geoip2 import GeoIP2
from geoip2.errors import AddressNotFoundError
from user_agents import parse


def get_client_ip_from_request_meta(request_meta: dict) -> str:
    x_forwarded_for = request_meta.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request_meta.get("REMOTE_ADDR")
    return ip


def get_country_from_request_meta(request_meta: dict) -> str:
    geo_ip = GeoIP2()
    ip = get_client_ip_from_request_meta(request_meta)
    try:
        country = geo_ip.country_name(ip)
    except AddressNotFoundError:
        country = None
    return country or "Unknown"


def get_page_view_metadata_from_request_meta(request_meta: dict) -> dict:
    metadata = {}
    user_agent_string = request_meta.get("HTTP_USER_AGENT")
    user_agent = parse(user_agent_string)
    if user_agent:
        metadata["browser"] = user_agent.browser.family
        metadata["os"] = user_agent.os.family
        metadata["device"] = user_agent.device.family
        metadata["country"] = get_country_from_request_meta(request_meta)
    return metadata
