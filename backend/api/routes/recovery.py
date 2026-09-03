from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["recovery"])


@router.get("/recovery-cases")
def recovery_cases() -> list[dict]:
    return [
        {
            "customer": "Rahul",
            "amount": 14999,
            "reason": "Low balance",
            "score": 91,
            "action": "Retry",
            "status": "Pending",
        },
        {
            "customer": "Aditi",
            "amount": 5999,
            "reason": "Card expired",
            "score": 84,
            "action": "Send payment link",
            "status": "Contacted",
        },
        {
            "customer": "ABC Ltd",
            "amount": 250000,
            "reason": "Overdue",
            "score": 42,
            "action": "Escalate",
            "status": "Escalated",
        },
    ]
