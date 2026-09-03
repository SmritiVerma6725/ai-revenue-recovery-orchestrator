from backend.data.synthetic import build_demo_summary, build_demo_transactions


def test_demo_summary_numbers() -> None:
    summary = build_demo_summary()

    assert summary["revenue_at_risk"] == 14999 + 5999 + 250000 + 9999
    assert summary["recoverable_amount"] > 0
    assert summary["recovered_amount"] > 0
    assert 0 < summary["recovery_rate"] < 100


def test_demo_transactions_cover_failure_types() -> None:
    transactions = build_demo_transactions()
    reasons = {item["failure_reason"] for item in transactions}

    assert reasons == {"insufficient_funds", "card_expired", "bank_timeout", "expired_card"}
    assert len(transactions) == 4
