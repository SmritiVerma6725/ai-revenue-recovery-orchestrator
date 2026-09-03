from backend.demo import build_audit_trail, build_recovery_timeline


def test_audit_trail() -> None:
    data = build_audit_trail()
    assert len(data) >= 3
    assert data[0]["event"] == "payment.failed"


def test_recovery_timeline() -> None:
    steps = build_recovery_timeline()
    assert steps[0]["step"] == "Payment failed"
    assert steps[-1]["step"] == "Workflow stopped"
