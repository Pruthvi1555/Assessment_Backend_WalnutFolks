# app/main.py
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from rq import Queue
from rq import Retry
from redis import Redis
from .db import engine


REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
redis_conn = Redis.from_url(REDIS_URL)
q = Queue('transactions', connection=redis_conn)


app = FastAPI()


class WebhookIn(BaseModel):
    transaction_id: str
    source_account: str
    destination_account: str
    amount: float
    currency: str


@app.get('/')
def health():
    return {"status": "HEALTHY", "current_time": datetime.utcnow().isoformat() + 'Z'}


@app.post('/v1/webhooks/transactions', status_code=202)
def receive_webhook(payload: WebhookIn):
    # Quick path: insert row (idempotent via unique constraint) and enqueue job only for new insert
    with engine.begin() as conn:
        try:
            conn.execute(text(
            """
            INSERT INTO transactions (transaction_id, source_account, destination_account, amount, currency, status)
            VALUES (:tx, :src, :dst, :amt, :cur, 'PROCESSING')
            """
        ), {
            'tx': payload.transaction_id,
            'src': payload.source_account,
            'dst': payload.destination_account,
            'amt': payload.amount,
            'cur': payload.currency
        })
            # enqueue job only when insert succeeded
            q.enqueue('app.worker.process_transaction', payload.transaction_id, job_timeout=600, retry=Retry(max=3))

            return {}
        except IntegrityError:
            # Duplicate tx — already exists. Do not enqueue another job.
            return {}


@app.get('/v1/transactions/{transaction_id}')
def get_transaction(transaction_id: str):
    with engine.begin() as conn:
        row = conn.execute(text(
            "SELECT transaction_id, source_account, destination_account, amount, currency, status, created_at, processed_at FROM transactions WHERE transaction_id = :tx"
        ), {'tx': transaction_id}).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail='Transaction not found')
        return dict(row._mapping)