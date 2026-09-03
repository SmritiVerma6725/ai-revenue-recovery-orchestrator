from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/dashboard")
def dashboard() -> dict:
    return {
        "revenue_at_risk": 2500000,
        "recoverable_amount": 1680000,
        "recovered_amount": 873450,
        "recovery_rate": 51.9,
        "transactions_analyzed": 10000,
        "recoverable_cases": 2840,
        "failure_reasons": [
            {"label": "Insufficient funds", "value": 34},
            {"label": "Card expired", "value": 22},
            {"label": "Bank timeout", "value": 18},
            {"label": "Subscription failed", "value": 16},
            {"label": "Overdue invoice", "value": 10},
        ],
    }
