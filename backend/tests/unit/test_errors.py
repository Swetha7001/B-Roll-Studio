"""Unit tests for Standard Error Schema and Exception Handlers."""
import pytest
from app.core.errors import (
    AppError, EmptyScriptError, IdempotencyConflictError, NotFoundError,
    SilentAudioError, UnsupportedMediaTypeError, ValidationError
)


def test_app_error_serialization():
    err = AppError(code="CUSTOM_TEST_CODE", message="Test readable message", details={"field": "test"})
    data = err.to_dict()
    assert "error" in data
    assert data["error"]["code"] == "CUSTOM_TEST_CODE"
    assert data["error"]["message"] == "Test readable message"
    assert data["error"]["retryable"] is False
    assert data["error"]["details"] == {"field": "test"}


def test_typed_exceptions():
    val_err = ValidationError("Field missing", details={"param": "script"})
    assert val_err.code == "VALIDATION_ERROR"
    assert val_err.status_code == 422

    empty_err = EmptyScriptError()
    assert empty_err.code == "EMPTY_SCRIPT_ERROR"
    assert empty_err.status_code == 400

    idem_err = IdempotencyConflictError()
    assert idem_err.code == "IDEMPOTENCY_CONFLICT"
    assert idem_err.status_code == 409

    media_err = UnsupportedMediaTypeError()
    assert media_err.code == "UNSUPPORTED_MEDIA_TYPE"
    assert media_err.status_code == 415

    silent_err = SilentAudioError()
    assert silent_err.code == "SILENT_AUDIO_DETECTED"
    assert silent_err.status_code == 400
