"""Thin HTTP routes — parse request, call services, return JSON."""

from __future__ import annotations

import os

from flask import Blueprint, current_app, g, jsonify, request

from core.errors import AppError, ForbiddenError, ValidationError
from core.health import build_health_payload
from core.log_analyzer import analyze_log_file, analyze_log_text
from core.models import CreateDocumentCommand, CreateRunCommand, UpdateTestCaseCommand
from integrations.ai_client import build_ai_client

api_bp = Blueprint("api", __name__, url_prefix="/api")


def _require_log_analyze_access() -> None:
    """Gate for AI log analysis: feature flag + admin token (required outside tests)."""
    if os.getenv("LOG_ANALYZE_ENABLED", "1").strip() == "0":
        raise ForbiddenError()
    expected = os.getenv("LOG_ANALYZE_ADMIN_TOKEN", "").strip()
    testing = bool(current_app.config.get("TESTING"))
    if not expected:
        # Pytest convenience only — production/local must set LOG_ANALYZE_ADMIN_TOKEN.
        if testing:
            return
        raise ForbiddenError()
    provided = request.headers.get("X-Admin-Token", "").strip()
    if provided != expected:
        raise ForbiddenError()


def _svc(name: str):
    return current_app.extensions[name]


@api_bp.get("/health")
def health():
    """Public liveness/readiness for UptimeRobot and local watchers.

    Always HTTP 200 when the process is up; ``status`` may be ``ok`` / ``degraded`` / ``fail``.
    UptimeRobot keyword monitor: expect ``\"status\":\"ok\"`` or ``\"api\":\"qa-assistant\"``.
    """
    payload = build_health_payload(current_app)
    return jsonify(payload)


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


@api_bp.post("/documents/upload")
def upload_document():
    """Multipart upload: extract text + persist to Storage/local + document meta."""
    if "file" not in request.files:
        raise ValidationError(code="VALIDATION_ERROR", message="multipart field 'file' is required")
    upload = request.files["file"]
    filename = (upload.filename or "").strip()
    if not filename:
        raise ValidationError(code="VALIDATION_ERROR", message="filename is required")
    data = upload.read()
    doc, text, char_count = _svc("document_service").upload_and_extract(
        user_id=g.user_id,
        filename=filename,
        data=data,
        mime_type=upload.mimetype,
    )
    return (
        jsonify(
            {
                "document": doc.to_dict(),
                "text": text,
                "char_count": char_count,
            }
        ),
        201,
    )


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
    requirements_text = (data.get("requirements_text") or "").strip() or None

    # Build per-request so tests can swap app.extensions["ai_client"].
    gen_svc = GenerationService(
        current_app.extensions["runs_repo"],
        current_app.extensions["docs_repo"],
        current_app.extensions["cases_repo"],
        current_app.extensions.get("ai_client"),
        current_app.extensions.get("document_service"),
        rag_service=current_app.extensions.get("rag_service"),
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


@api_bp.post("/chat")
def chat_requirements():
    """RAG chat over indexed document chunks."""
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or data.get("message") or "").strip()
    if len(question) < 2:
        raise ValidationError(code="VALIDATION_ERROR", message="question is required")
    document_id = (data.get("document_id") or "").strip() or None
    rag = current_app.extensions.get("rag_service")
    ai = current_app.extensions.get("ai_client")
    if rag is None:
        raise AppError(code="INTERNAL_ERROR", status_code=500)
    if ai is None:
        raise AppError(code="MISSING_TOKEN", status_code=503)
    result = rag.chat(
        user_id=g.user_id,
        question=question,
        document_id=document_id,
        ai_generate=ai.generate,
    )
    return jsonify(result)


@api_bp.post("/rag/index-cases")
def index_reviewed_cases_to_rag():
    """Index only human-reviewed cases into case_chunks (explicit opt-in)."""
    data = request.get_json(silent=True) or {}
    case_ids = data.get("case_ids") or []
    if case_ids is not None and not isinstance(case_ids, list):
        raise ValidationError(code="VALIDATION_ERROR", message="case_ids must be a list")
    run_id = (data.get("run_id") or "").strip() or None
    ids = [str(x).strip() for x in case_ids if str(x).strip()]
    count = _svc("testcase_service").index_reviewed_to_rag(
        g.user_id,
        case_ids=ids or None,
        run_id=run_id,
    )
    return jsonify({"indexed": count, "source_type": "approved_case"})


@api_bp.post("/rag/templates")
def upsert_rag_templates():
    """Upload style templates (positive/negative/boundary) into case_chunks."""
    from core.rag_models import IndexCaseChunkCommand

    data = request.get_json(silent=True) or {}
    items = data.get("items") or data.get("templates") or []
    if not isinstance(items, list) or not items:
        raise ValidationError(code="VALIDATION_ERROR", message="items[] required")
    rag = current_app.extensions.get("rag_service")
    embedder = current_app.extensions.get("embedding_client")
    if rag is None or embedder is None or not getattr(rag, "enabled", False):
        raise AppError(code="INTERNAL_ERROR", status_code=500, message="RAG unavailable")

    commands: list[IndexCaseChunkCommand] = []
    for raw in items:
        if not isinstance(raw, dict):
            continue
        name = str(raw.get("name") or "").strip()
        step = str(raw.get("step") or "").strip()
        expected = str(raw.get("expected_result") or "").strip()
        source_type = str(raw.get("source_type") or "template").strip()
        if source_type not in {"template", "anti_example", "approved_case"}:
            source_type = "template"
        tags = raw.get("tags") or []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]
        content = f"{name}\n{step}\n{expected}".strip()
        if not content:
            continue
        emb = embedder.embed(content)
        commands.append(
            IndexCaseChunkCommand(
                user_id=g.user_id,
                source_type=source_type,
                name=name or "template",
                content=content,
                embedding=emb,
                status=str(raw.get("status") or "Approved"),
                step=step,
                expected_result=expected,
                tags=tuple(str(t) for t in tags),
                metadata={"kind": raw.get("kind") or "style"},
            )
        )
    if not commands:
        raise ValidationError(code="VALIDATION_ERROR", message="No valid templates")
    count = rag.index_case_commands(commands)
    return jsonify({"indexed": count})


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
    scenario = (data.get("scenario") or "general").strip() or "general"
    try:
        max_lines = int(data.get("max_lines", 200))
    except (TypeError, ValueError) as exc:
        raise ValidationError(code="VALIDATION_ERROR", message="max_lines must be integer") from exc

    if inline:
        result = analyze_log_text(inline, ai, source="inline", scenario=scenario)
    else:
        result = analyze_log_file(ai, max_lines=max_lines, scenario=scenario)
    return jsonify(result.to_dict())
