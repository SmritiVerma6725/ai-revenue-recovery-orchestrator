from __future__ import annotations

from datetime import datetime


def build_demo_customers() -> list[dict]:
    return [
        {
            "id": "CUST-001",
            "name": "Rahul Sharma",
            "email": "rahul@example.com",
            "phone": "9999999999",
            "customer_since": "2023-01-12T00:00:00",
            "total_transactions": 12,
            "successful_transactions": 11,
            "failed_transactions": 1,
            "lifetime_value": 58000,
            "last_seen_at": "2026-08-20T12:00:00",
        },
        {
            "id": "CUST-002",
            "name": "Aditi Nair",
            "email": "aditi@example.com",
            "phone": "8888888888",
            "customer_since": "2022-08-05T00:00:00",
            "total_transactions": 9,
            "successful_transactions": 8,
            "failed_transactions": 1,
            "lifetime_value": 42000,
            "last_seen_at": "2026-08-19T18:30:00",
        },
        {
            "id": "CUST-003",
            "name": "ABC Ltd",
            "email": "finance@abcltd.com",
            "phone": "7777777777",
            "customer_since": "2021-02-01T00:00:00",
            "total_transactions": 74,
            "successful_transactions": 68,
            "failed_transactions": 6,
            "lifetime_value": 540000,
            "last_seen_at": "2026-08-18T09:15:00",
        },
        {
            "id": "CUST-004",
            "name": "Meera Singh",
            "email": "meera@example.com",
            "phone": "6666666666",
            "customer_since": "2024-03-08T00:00:00",
            "total_transactions": 5,
            "successful_transactions": 3,
            "failed_transactions": 2,
            "lifetime_value": 26000,
            "last_seen_at": "2026-08-20T08:40:00",
        },
    ]


def build_demo_transactions() -> list[dict]:
    return [
        {
            "id": "TX-1001",
            "customer_id": "CUST-001",
            "amount": 14999,
            "currency": "INR",
            "payment_method": "card",
            "status": "failed",
            "created_at": "2026-08-20T09:00:00",
            "failure_code": "BAD_REQUEST_ERROR",
            "failure_reason": "insufficient_funds",
            "retry_count": 0,
        },
        {
            "id": "TX-1002",
            "customer_id": "CUST-002",
            "amount": 5999,
            "currency": "INR",
            "payment_method": "upi",
            "status": "failed",
            "created_at": "2026-08-19T14:30:00",
            "failure_code": "UPI_ERROR",
            "failure_reason": "card_expired",
            "retry_count": 1,
        },
        {
            "id": "TX-1003",
            "customer_id": "CUST-003",
            "amount": 250000,
            "currency": "INR",
            "payment_method": "netbanking",
            "status": "failed",
            "created_at": "2026-08-18T15:15:00",
            "failure_code": "GATEWAY_ERROR",
            "failure_reason": "bank_timeout",
            "retry_count": 2,
        },
        {
            "id": "TX-1004",
            "customer_id": "CUST-004",
            "amount": 9999,
            "currency": "INR",
            "payment_method": "card",
            "status": "failed",
            "created_at": "2026-08-18T10:00:00",
            "failure_code": "CARD_ERROR",
            "failure_reason": "expired_card",
            "retry_count": 0,
        },
    ]


def build_demo_summary() -> dict:
    customers = build_demo_customers()
    transactions = build_demo_transactions()
    revenue_at_risk = sum(item["amount"] for item in transactions)
    recoverable_amount = int(revenue_at_risk * 0.67)
    recovered_amount = int(revenue_at_risk * 0.35)

    return {
        "customers": customers,
        "transactions": transactions,
        "revenue_at_risk": revenue_at_risk,
        "recoverable_amount": recoverable_amount,
        "recovered_amount": recovered_amount,
        "recovery_rate": round((recovered_amount / revenue_at_risk) * 100, 1),
        "failure_reasons": {
            "insufficient_funds": 1,
            "card_expired": 1,
            "bank_timeout": 1,
            "expired_card": 1,
        },
    }
