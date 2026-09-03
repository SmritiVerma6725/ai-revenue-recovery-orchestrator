import importlib

from backend.config.settings import settings
from backend.services.retry_scheduler import RetryScheduler


def test_retry_scheduler_processes_pending_retries() -> None:
    scheduler = RetryScheduler()
    result = scheduler.schedule_retry("TX-5001", 15000, delay_seconds=0)
    assert result["status"] == "scheduled"
    assert len(scheduler.list_pending()) == 1

    processed = scheduler.process_pending()
    assert processed[0]["transaction_id"] == "TX-5001"
    assert len(scheduler.list_pending()) == 0


def test_settings_reads_environment(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("RAZORPAY_KEY_ID", "rzp_test_123")
    monkeypatch.setenv("RAZORPAY_KEY_SECRET", "secret_456")

    module = importlib.import_module("backend.config.settings")
    importlib.reload(module)

    assert module.settings.app_env == "production"
    assert module.settings.razorpay_key_id == "rzp_test_123"
    assert module.settings.razorpay_key_secret == "secret_456"
