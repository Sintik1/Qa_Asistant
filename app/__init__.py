"""Flask application factory."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from flask import Flask, g, jsonify, request
from flask_cors import CORS

from app.auth import verify_supabase_access_token
from core.errors import AppError, UnauthorizedError
from core.messages import ERROR_MESSAGES
from core.services import DocumentService, RunService, SettingsService, TestCaseService
from infrastructure.memory_store import (
    MemoryDocumentRepository,
    MemoryRunRepository,
    MemorySettingsRepository,
    MemoryTestCaseRepository,
)
from integrations.ai_client import build_ai_client, load_ai_settings

PUBLIC_API_PATHS = frozenset({"/api/health", "/api/ai/ping"})


def _cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:8080")
    return [o.strip() for o in raw.split(",") if o.strip()]


def create_app(testing: bool = False) -> Flask:
    load_dotenv()
    app = Flask(__name__)
    app.config["TESTING"] = testing

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": _cors_origins(),
                "methods": ["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": [
                    "Authorization",
                    "Content-Type",
                    "X-User-Id",
                    "X-Skip-Auth",
                ],
                "expose_headers": ["Content-Type"],
                "supports_credentials": True,
            }
        },
    )

    docs_repo = MemoryDocumentRepository()
    runs_repo = MemoryRunRepository()
    cases_repo = MemoryTestCaseRepository()
    settings_repo = MemorySettingsRepository()
    ai_settings = load_ai_settings()
    ai_client = build_ai_client(ai_settings)

    app.extensions["docs_repo"] = docs_repo
    app.extensions["runs_repo"] = runs_repo
    app.extensions["cases_repo"] = cases_repo
    app.extensions["settings_repo"] = settings_repo
    app.extensions["document_service"] = DocumentService(docs_repo)
    app.extensions["run_service"] = RunService(runs_repo, docs_repo)
    app.extensions["testcase_service"] = TestCaseService(cases_repo, runs_repo)
    app.extensions["settings_service"] = SettingsService(settings_repo)
    app.extensions["ai_settings"] = ai_settings
    app.extensions["ai_client"] = ai_client

    from app.routes import api_bp

    app.register_blueprint(api_bp)

    @app.before_request
    def load_user() -> None:
        if request.method == "OPTIONS":
            return
        if not request.path.startswith("/api/"):
            return
        if request.path in PUBLIC_API_PATHS:
            return

        auth = request.headers.get("Authorization", "")
        bearer = auth[7:].strip() if auth.startswith("Bearer ") else ""

        if bearer:
            try:
                user = verify_supabase_access_token(bearer)
            except UnauthorizedError:
                raise UnauthorizedError() from None
            g.user_id = user.user_id
            g.access_token = bearer
            g.user_email = user.email
            return

        # Dev/test bypass only — never trusted in production.
        if testing or os.getenv("AUTH_DEV_BYPASS", "").strip() == "1":
            if request.headers.get("X-Skip-Auth") == "1":
                raise UnauthorizedError()
            user_id = request.headers.get("X-User-Id", "").strip()
            if not user_id and testing:
                user_id = "00000000-0000-4000-8000-000000000001"
            if user_id:
                g.user_id = user_id
                g.access_token = None
                g.user_email = None
                return

        raise UnauthorizedError()

    @app.errorhandler(AppError)
    def handle_app_error(exc: AppError):
        return jsonify(exc.to_dict()), exc.status_code

    @app.errorhandler(404)
    def handle_404(_exc):
        return jsonify(AppError(code="NOT_FOUND", status_code=404).to_dict()), 404

    @app.errorhandler(405)
    def handle_405(_exc):
        return (
            jsonify(
                {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": ERROR_MESSAGES["VALIDATION_ERROR"],
                    }
                }
            ),
            405,
        )

    @app.errorhandler(Exception)
    def handle_unexpected(_exc):
        if app.config.get("TESTING"):
            raise
        return jsonify(AppError(code="INTERNAL_ERROR", status_code=500).to_dict()), 500

    return app
