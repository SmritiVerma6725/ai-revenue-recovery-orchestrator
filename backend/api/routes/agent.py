from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["agent"])


@router.get("/agent/decision")
def agent_decision() -> dict:
    return {
        "transaction_id": "TX82731",
        "recovery_probability": 91,
        "diagnosis": "Temporary insufficient funds with a strong recent payment history.",
        "decision": "Retry in 24 hours",
        "reason": "Customer has 8 previous successful payments.",
        "guardrail": "Maximum retries = 2",
        "status": "pending",
    }
