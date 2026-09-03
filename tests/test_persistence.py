from backend.storage.recovery_store import RecoveryStore


def test_recovery_store_round_trip(tmp_path) -> None:
    db_path = tmp_path / "recovery.db"
    store = RecoveryStore(db_path)

    case_id = store.save_case(
        {
            "transaction_id": "TX-2001",
            "customer_id": "CUST-001",
            "recovery_score": 82,
            "recoverable_amount": 15000,
            "status": "open",
            "recommended_action": "retry",
            "reasons": ["insufficient_funds"],
        }
    )

    stored_case = store.get_case(case_id)
    assert stored_case["transaction_id"] == "TX-2001"
    assert stored_case["customer_id"] == "CUST-001"

    store.add_audit_log(
        {
            "recovery_case_id": case_id,
            "event": "payment.failed",
            "agent_reasoning": "Temporary issue",
            "action": "retry",
            "result": "queued",
        }
    )

    audit_logs = store.list_audit_logs(case_id)
    assert len(audit_logs) == 1
    assert audit_logs[0]["event"] == "payment.failed"
    assert len(store.list_cases()) == 1
