from pathlib import Path

from app.services.audit import AuditService


def test_audit_service_uses_local_fallback_when_no_loop(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    service = AuditService()
    result = service.dispatch({"event": "health_check", "success": True})

    fallback_file = Path("logs") / "audit-fallback.log"

    assert result.fallback_used is True
    assert fallback_file.exists()
    assert "health_check" in fallback_file.read_text(encoding="utf-8")
