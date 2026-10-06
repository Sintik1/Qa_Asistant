"""PostgREST client error mapping (CI/CD ДЗ шаг 8)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
import pytest

from core.errors import AppError
from infrastructure.supabase_rest import SupabaseRestClient, SupabaseRestConfig


@pytest.fixture()
def rest_client() -> SupabaseRestClient:
    config = SupabaseRestConfig(
        base_url="https://example.supabase.co",
        anon_key="anon-key",
        service_role_key="service-role-key",
    )
    return SupabaseRestClient(config)


def test_select_maps_transport_error_to_api_unavailable(rest_client: SupabaseRestClient):
    with patch("infrastructure.supabase_rest.httpx.request") as mock_request:
        mock_request.side_effect = httpx.ProxyError("403 Forbidden")
        with pytest.raises(AppError) as exc:
            rest_client.select("runs")
    assert exc.value.code == "API_UNAVAILABLE"
    assert exc.value.status_code == 503


def test_select_maps_timeout_to_api_unavailable(rest_client: SupabaseRestClient):
    with patch("infrastructure.supabase_rest.httpx.request") as mock_request:
        mock_request.side_effect = httpx.TimeoutException("timed out")
        with pytest.raises(AppError) as exc:
            rest_client.select("runs")
    assert exc.value.code == "API_UNAVAILABLE"
    assert exc.value.status_code == 503


def test_select_maps_postgrest_5xx_to_api_unavailable(rest_client: SupabaseRestClient):
    response = MagicMock()
    response.status_code = 502
    response.text = "bad gateway"
    with patch("infrastructure.supabase_rest.httpx.request", return_value=response):
        with pytest.raises(AppError) as exc:
            rest_client.select("runs")
    assert exc.value.code == "API_UNAVAILABLE"
    assert exc.value.status_code == 503


def test_select_maps_postgrest_401_to_forbidden(rest_client: SupabaseRestClient):
    response = MagicMock()
    response.status_code = 401
    response.text = "JWT expired"
    with patch("infrastructure.supabase_rest.httpx.request", return_value=response):
        with pytest.raises(AppError) as exc:
            rest_client.select("runs")
    assert exc.value.code == "FORBIDDEN"
    assert exc.value.status_code == 403


def test_select_success_returns_json_list(rest_client: SupabaseRestClient):
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = [{"id": "1"}]
    with patch("infrastructure.supabase_rest.httpx.request", return_value=response):
        rows = rest_client.select("runs", params={"user_id": "eq.u1"})
    assert rows == [{"id": "1"}]
