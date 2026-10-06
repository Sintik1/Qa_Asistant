"""Minimal PostgREST client for Supabase (JWT user or service role)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import httpx
from flask import g, has_app_context, has_request_context

from core.errors import AppError


@dataclass(frozen=True)
class SupabaseRestConfig:
    base_url: str
    anon_key: str
    service_role_key: str | None = None

    @property
    def rest_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/rest/v1"

    @classmethod
    def from_env(cls) -> SupabaseRestConfig | None:
        url = (os.getenv("SUPABASE_URL") or "").strip()
        anon = (os.getenv("SUPABASE_ANON_KEY") or "").strip()
        service = (os.getenv("SUPABASE_SERVICE_ROLE_KEY") or "").strip()
        if not url or url.startswith("your_"):
            return None
        if (not anon or anon.startswith("your_")) and (not service or service.startswith("your_")):
            return None
        return cls(
            base_url=url,
            anon_key=anon if anon and not anon.startswith("your_") else service,
            service_role_key=service if service and not service.startswith("your_") else None,
        )


class SupabaseRestClient:
    """HTTP helper; prefers request JWT so RLS applies, else service role."""

    def __init__(self, config: SupabaseRestConfig, timeout: float = 30.0) -> None:
        self._config = config
        self._timeout = timeout

    def _auth_bearer(self) -> str:
        if has_request_context():
            token = getattr(g, "access_token", None)
            if token:
                return str(token)
        if self._config.service_role_key:
            return self._config.service_role_key
        return self._config.anon_key

    def _headers(self, *, prefer: str | None = None) -> dict[str, str]:
        headers = {
            "apikey": self._config.anon_key,
            "Authorization": f"Bearer {self._auth_bearer()}",
            "Content-Type": "application/json",
        }
        if prefer:
            headers["Prefer"] = prefer
        # Help PostgREST return useful errors
        if has_app_context() and has_request_context():
            request_id = getattr(g, "request_id", None)
            if request_id:
                headers["X-Request-Id"] = str(request_id)
        return headers

    def _send(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, str] | None = None,
        json: Any = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        try:
            return httpx.request(
                method,
                url,
                params=params,
                json=json,
                headers=headers,
                timeout=self._timeout,
            )
        except httpx.TimeoutException as exc:
            raise AppError(code="API_UNAVAILABLE", status_code=503) from exc
        except httpx.HTTPError as exc:
            # Proxy/DNS/connection failures must not surface as unhandled 500.
            raise AppError(code="API_UNAVAILABLE", status_code=503) from exc

    def select(
        self,
        table: str,
        *,
        params: dict[str, str] | None = None,
    ) -> list[dict[str, Any]]:
        response = self._send(
            "GET",
            f"{self._config.rest_url}/{table}",
            params=params or {},
            headers=self._headers(),
        )
        self._raise(response, f"SELECT {table}")
        data = response.json()
        return data if isinstance(data, list) else []

    def insert(
        self,
        table: str,
        row: dict[str, Any] | list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        response = self._send(
            "POST",
            f"{self._config.rest_url}/{table}",
            json=row,
            headers=self._headers(prefer="return=representation"),
        )
        self._raise(response, f"INSERT {table}")
        data = response.json()
        return data if isinstance(data, list) else [data]

    def upsert(
        self,
        table: str,
        row: dict[str, Any],
        *,
        on_conflict: str,
    ) -> list[dict[str, Any]]:
        response = self._send(
            "POST",
            f"{self._config.rest_url}/{table}",
            params={"on_conflict": on_conflict},
            json=row,
            headers=self._headers(prefer="resolution=merge-duplicates,return=representation"),
        )
        self._raise(response, f"UPSERT {table}")
        data = response.json()
        return data if isinstance(data, list) else [data]

    def patch(
        self,
        table: str,
        *,
        params: dict[str, str],
        patch: dict[str, Any],
    ) -> list[dict[str, Any]]:
        response = self._send(
            "PATCH",
            f"{self._config.rest_url}/{table}",
            params=params,
            json=patch,
            headers=self._headers(prefer="return=representation"),
        )
        self._raise(response, f"PATCH {table}")
        data = response.json()
        return data if isinstance(data, list) else [data]

    def delete(self, table: str, *, params: dict[str, str]) -> None:
        response = self._send(
            "DELETE",
            f"{self._config.rest_url}/{table}",
            params=params,
            headers=self._headers(),
        )
        self._raise(response, f"DELETE {table}")

    def rpc(self, fn_name: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
        """Call a PostgREST / PostgreSQL function."""
        response = self._send(
            "POST",
            f"{self._config.rest_url}/rpc/{fn_name}",
            json=payload,
            headers=self._headers(prefer="return=representation"),
        )
        self._raise(response, f"RPC {fn_name}")
        data = response.json()
        if data is None:
            return []
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return [data]
        return []

    @staticmethod
    def _raise(response: httpx.Response, action: str) -> None:
        if response.status_code < 400:
            return
        if response.status_code >= 500:
            raise AppError(code="API_UNAVAILABLE", status_code=503)
        # 4xx from PostgREST (RLS/auth) — keep actionable message without leaking body.
        raise AppError(
            code="FORBIDDEN" if response.status_code in {401, 403} else "VALIDATION_ERROR",
            status_code=403 if response.status_code in {401, 403} else 422,
            message=f"Supabase REST {action} failed: HTTP {response.status_code}",
        )
