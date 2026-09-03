from __future__ import annotations

import threading
import time
from collections import deque
from datetime import datetime, timedelta, timezone


class RetryScheduler:
    def __init__(self) -> None:
        self._pending: deque[dict] = deque()
        self._lock = threading.Lock()

    def schedule_retry(self, transaction_id: str, amount: int, delay_seconds: int = 60) -> dict:
        scheduled_at = datetime.now(timezone.utc) + timedelta(seconds=delay_seconds)
        entry = {
            "transaction_id": transaction_id,
            "amount": amount,
            "scheduled_at": scheduled_at,
            "status": "scheduled",
        }
        with self._lock:
            self._pending.append(entry)
        return {"status": "scheduled", "transaction_id": transaction_id, "run_at": scheduled_at.isoformat()}

    def list_pending(self) -> list[dict]:
        with self._lock:
            return [dict(item) for item in list(self._pending)]

    def process_pending(self) -> list[dict]:
        now = datetime.now(timezone.utc)
        processed: list[dict] = []
        with self._lock:
            remaining = deque()
            while self._pending:
                item = self._pending.popleft()
                if item["scheduled_at"] <= now:
                    processed.append({**item, "status": "processed"})
                else:
                    remaining.append(item)
            self._pending = remaining
        return processed

    def run_loop(self, interval_seconds: int = 5) -> None:
        while True:
            self.process_pending()
            time.sleep(interval_seconds)
