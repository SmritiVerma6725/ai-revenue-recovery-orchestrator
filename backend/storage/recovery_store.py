from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path


class RecoveryStore:
    def __init__(self, db_path: str | Path = "backend/data/recovery.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_db()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_db(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS recovery_cases (
                    id TEXT PRIMARY KEY,
                    transaction_id TEXT NOT NULL,
                    customer_id TEXT NOT NULL,
                    recovery_score INTEGER NOT NULL,
                    recoverable_amount INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    recommended_action TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    closed_at TEXT,
                    reasons TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id TEXT PRIMARY KEY,
                    recovery_case_id TEXT NOT NULL,
                    event TEXT NOT NULL,
                    agent_reasoning TEXT NOT NULL,
                    action TEXT NOT NULL,
                    result TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (recovery_case_id) REFERENCES recovery_cases (id)
                )
                """
            )
            connection.commit()

    def _iso_now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def save_case(self, case_data: dict) -> str:
        case_id = str(uuid.uuid4())
        created_at = self._iso_now()
        row = {
            "id": case_id,
            "transaction_id": case_data["transaction_id"],
            "customer_id": case_data["customer_id"],
            "recovery_score": int(case_data["recovery_score"]),
            "recoverable_amount": int(case_data["recoverable_amount"]),
            "status": case_data.get("status", "open"),
            "recommended_action": case_data.get("recommended_action", "retry"),
            "created_at": created_at,
            "closed_at": case_data.get("closed_at"),
            "reasons": json.dumps(case_data.get("reasons", [])),
        }
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO recovery_cases (
                    id, transaction_id, customer_id, recovery_score,
                    recoverable_amount, status, recommended_action,
                    created_at, closed_at, reasons
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["id"],
                    row["transaction_id"],
                    row["customer_id"],
                    row["recovery_score"],
                    row["recoverable_amount"],
                    row["status"],
                    row["recommended_action"],
                    row["created_at"],
                    row["closed_at"],
                    row["reasons"],
                ),
            )
            connection.commit()
        return case_id

    def get_case(self, case_id: str) -> dict | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM recovery_cases WHERE id = ?",
                (case_id,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_case(row)

    def list_cases(self) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM recovery_cases ORDER BY created_at DESC").fetchall()
        return [self._row_to_case(row) for row in rows]

    def add_audit_log(self, log_data: dict) -> str:
        log_id = str(uuid.uuid4())
        row = {
            "id": log_id,
            "recovery_case_id": log_data["recovery_case_id"],
            "event": log_data["event"],
            "agent_reasoning": log_data["agent_reasoning"],
            "action": log_data["action"],
            "result": log_data["result"],
            "timestamp": log_data.get("timestamp", self._iso_now()),
        }
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO audit_logs (id, recovery_case_id, event, agent_reasoning, action, result, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["id"],
                    row["recovery_case_id"],
                    row["event"],
                    row["agent_reasoning"],
                    row["action"],
                    row["result"],
                    row["timestamp"],
                ),
            )
            connection.commit()
        return log_id

    def list_audit_logs(self, recovery_case_id: str) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM audit_logs WHERE recovery_case_id = ? ORDER BY timestamp ASC",
                (recovery_case_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def _row_to_case(row: sqlite3.Row) -> dict:
        case = dict(row)
        case["reasons"] = json.loads(case.get("reasons", "[]"))
        return case
