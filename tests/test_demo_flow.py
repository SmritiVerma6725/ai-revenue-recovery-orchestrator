from backend.demo import build_agent_decision, build_demo_dashboard, build_recovery_cases, build_revenue_trend, reset_demo_state, simulate_recovery


def test_demo_dashboard() -> None:
    data = build_demo_dashboard()
    assert data["revenue_at_risk"] > 0
    assert data["recovery_rate"] > 0


def test_demo_recovery_cases() -> None:
    cases = build_recovery_cases()
    assert len(cases) >= 1
    assert all("score" in case for case in cases)
    assert all("action" in case for case in cases)


def test_demo_recovery_changes_displayed_amounts() -> None:
    before = build_demo_dashboard()
    after = simulate_recovery(10000)

    assert after["recovered_amount"] == before["recovered_amount"] + 10000
    assert after["revenue_at_risk"] == before["revenue_at_risk"] - 10000
    assert after["recovery_rate"] > before["recovery_rate"]
    reset_demo_state()


def test_revenue_trend_covers_month_and_matches_total() -> None:
    trend = build_revenue_trend()

    assert len(trend) == 30
    assert trend[0]["day"] == 1
    assert trend[-1]["day"] == 30
    assert trend[-1]["cumulative_recovered"] == build_demo_dashboard()["recovered_amount"]


def test_demo_agent_decision() -> None:
    result = build_agent_decision()
    assert "transaction_id" in result
    assert "diagnosis" in result
    assert "decision" in result
    assert "guardrail" in result
