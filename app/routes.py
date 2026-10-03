"""Thin HTTP routes — parse request, call services, return JSON."""

from __future__ import annotations

import os

from flask import Blueprint, current_app, g, jsonify, request

from core.errors import AppError, ForbiddenError, ValidationError
from core.log_analyzer import analyze_log_file, analyze_log_text
from core.models import CreateDocumentCommand, CreateRunCommand, UpdateTestCaseCommand
from integrations.ai_client import ai_status_dict, build_ai_client

api_bp = Blueprint("api", __name__, url_prefix="/api")


def _require_log_analyze_access() -> None:
    """Gate for AI log analysis: feature flag + optional admin token."""
    if os.getenv("LOG_ANALYZE_ENABLED", "1").strip() == "0":
        raise ForbiddenError()
    expected = os.getenv("LOG_ANALYZE_ADMIN_TOKEN", "").strip()
    if expected:
        provided = request.headers.get("X-Admin-Token", "").strip()
        if provided != expected:
            raise ForbiddenError()


def _svc(name: str):
    return current_app.extensions[name]


@api_bp.get("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "api": "qa-assistant",
            "mode": "hybrid-c",
            "ai": ai_status_dict(),
        }
    )


@api_bp.post("/ai/ping")
def ai_ping():
    """Smoke-call current AI provider (Ollama/Leopold) for local debug."""
    client = _svc("ai_client") or build_ai_client()
    if client is None:
        raise AppError(code="MISSING_TOKEN", status_code=503)
    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "Ответь одним словом: pong").strip()
    text = client.generate(
        system_prompt="Ты тестовый ассистент. Отвечай кратко.",
        user_content=prompt,
    )
    settings = _svc("ai_settings")
    return jsonify(
        {
            "provider": settings.provider,
            "model": settings.model,
            "reply": text,
        }
    )


@api_bp.get("/documents")
def list_documents():
    items = _svc("document_service").list_for_user(g.user_id)
    return jsonify({"items": [d.to_dict() for d in items]})


@api_bp.post("/documents")
def create_document():
    data = request.get_json(silent=True) or {}
    filename = (data.get("original_filename") or data.get("filename") or "").strip()
    if not filename:
        raise ValidationError(code="VALIDATION_ERROR", message="original_filename is required")
    try:
        size_bytes = int(data.get("size_bytes", 0))
    except (TypeError, ValueError) as exc:
        raise ValidationError(code="VALIDATION_ERROR", message="size_bytes must be integer") from exc

    doc = _svc("document_service").create(
        CreateDocumentCommand(
            user_id=g.user_id,
            original_filename=filename,
            size_bytes=size_bytes,
            mime_type=data.get("mime_type"),
            storage_path=data.get("storage_path"),
        )
    )
    return jsonify(doc.to_dict()), 201


@api_bp.get("/documents/<document_id>")
def get_document(document_id: str):
    doc = _svc("document_service").get(document_id, g.user_id)
    return jsonify(doc.to_dict())


@api_bp.get("/runs")
def list_runs():
    items = _svc("run_service").list_for_user(g.user_id)
    return jsonify({"items": [r.to_dict() for r in items]})


@api_bp.post("/runs")
def create_run():
    data = request.get_json(silent=True) or {}
    document_id = (data.get("document_id") or "").strip()
    if not document_id:
        raise ValidationError(code="VALIDATION_ERROR", message="document_id is required")
    run = _svc("run_service").create(
        CreateRunCommand(
            user_id=g.user_id,
            document_id=document_id,
            chunk_size=int(data.get("chunk_size", 4000)),
            chunk_overlap=int(data.get("chunk_overlap", 200)),
            chunk_method=str(data.get("chunk_method", "header")),
        )
    )
    return jsonify(run.to_dict()), 201


@api_bp.get("/runs/<run_id>")
def get_run(run_id: str):
    run = _svc("run_service").get(run_id, g.user_id)
    return jsonify(run.to_dict())


@api_bp.delete("/runs/<run_id>")
def delete_run(run_id: str):
    _svc("run_service").delete(run_id, g.user_id)
    return "", 204


@api_bp.get("/runs/<run_id>/test-cases")
def list_test_cases(run_id: str):
    items = _svc("testcase_service").list_for_run(run_id, g.user_id)
    return jsonify({"items": [c.to_dict() for c in items]})


@api_bp.post("/runs/<run_id>/generate")
def generate_run(run_id: str):
    """Run AI generation for an existing run; persist test cases."""
    from core.services import GenerationService

    data = request.get_json(silent=True) or {}
    requirements_text = (data.get("requirements_text") or "").strip()
    # Prefer client-extracted text; fallback to filename hint for thin MVP.
    if not requirements_text:
        run = _svc("run_service").get(run_id, g.user_id)
        doc = _svc("document_service").get(run.document_id, g.user_id)
        requirements_text = f"Документ: {doc.original_filename}"

    # Build per-request so tests can swap app.extensions["ai_client"].
    gen_svc = GenerationService(
        current_app.extensions["runs_repo"],
        current_app.extensions["docs_repo"],
        current_app.extensions["cases_repo"],
        current_app.extensions.get("ai_client"),
    )
    run, cases = gen_svc.generate(
        run_id,
        g.user_id,
        requirements_text=requirements_text,
        task_name=data.get("task_name"),
        prompt=data.get("prompt"),
    )
    return jsonify(
        {
            "run": run.to_dict(),
            "items": [c.to_dict() for c in cases],
        }
    )


@api_bp.patch("/test-cases/<case_id>")
def update_test_case(case_id: str):
    data = request.get_json(silent=True) or {}
    if not data:
        raise ValidationError(code="VALIDATION_ERROR", message="JSON body required")
    case = _svc("testcase_service").update(
        case_id,
        g.user_id,
        UpdateTestCaseCommand(
            name=data.get("name"),
            status=data.get("status"),
            step=data.get("step"),
            expected_result=data.get("expected_result"),
            sort_order=data.get("sort_order"),
        ),
    )
    return jsonify(case.to_dict())


@api_bp.get("/settings")
def get_settings():
    settings = _svc("settings_service").get(g.user_id)
    return jsonify(settings.to_dict())


@api_bp.patch("/settings")
def patch_settings():
    data = request.get_json(silent=True) or {}
    settings = _svc("settings_service").update(g.user_id, data)
    return jsonify(settings.to_dict())


@api_bp.post("/admin/analyze-logs")
def analyze_logs():
    """AI analysis of server log tail or inline log text (ops / homework)."""
    _require_log_analyze_access()
    data = request.get_json(silent=True) or {}
    ai = current_app.extensions.get("ai_client")
    inline = (data.get("text") or data.get("log_text") or "").strip()
    try:
        max_lines = int(data.get("max_lines", 200))
    except (TypeError, ValueError) as exc:
        raise ValidationError(
            code="VALIDATION_ERROR", message="max_lines must be integer"
        ) from exc

    if inline:
        result = analyze_log_text(inline, ai, source="inline")
    else:
        result = analyze_log_file(ai, max_lines=max_lines)
    return jsonify(result.to_dict())
