# app/worker.py
import time
from datetime import datetime
from sqlalchemy import text
from .db import engine
from rq import get_current_job




def process_transaction(transaction_id: str):
    """Background job: simulate processing the transaction.
    This function sleeps 30 seconds to simulate external calls, then updates DB.
    It also checks for already PROCESSED rows to maintain idempotency.
    """
    job = get_current_job()
    job_id = job.id if job else None
    with engine.begin() as conn:
        row = conn.execute(text("SELECT status FROM transactions WHERE transaction_id = :tx FOR UPDATE"), {'tx': transaction_id}).fetchone()
        if not row:
            # Unexpected: create a PROCESSING row so we can proceed
            conn.execute(text("INSERT INTO transactions (transaction_id, status, created_at) VALUES (:tx,'PROCESSING', now())"), {'tx': transaction_id})
        else:
            if row['status'] == 'PROCESSED':
            # already done — idempotent exit
                return


        try:
            # simulate external API call latency
            time.sleep(30)


            # Update to PROCESSED
            conn.execute(text("UPDATE transactions SET status='PROCESSED', processed_at = now(), last_error = NULL WHERE transaction_id = :tx"), {'tx': transaction_id})
        except Exception as exc:
            # mark failed and rethrow so RQ can retry according to its policy
            conn.execute(text("UPDATE transactions SET status='FAILED', last_error = :err WHERE transaction_id = :tx"), {'err': str(exc), 'tx': transaction_id})
            raise