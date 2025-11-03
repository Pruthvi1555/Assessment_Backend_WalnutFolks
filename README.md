TRANSACTION WEBHOOK SERVICE
===========================

This project implements a reliable webhook processor that receives transaction notifications from external payment providers (like Razorpay), acknowledges them instantly, and processes them asynchronously in the background using Redis queues and workers.


------------------------------------------------------------
FEATURES
------------------------------------------------------------
- Webhook Endpoint: POST /v1/webhooks/transactions
  Accepts incoming transaction payloads and responds immediately (202 Accepted).

- Health Check Endpoint: GET /
  Returns current health and timestamp of the service.

- Query Endpoint: GET /v1/transactions/{transaction_id}
  Retrieves transaction details and current processing status.

- Background Processing
  Webhooks are processed asynchronously by a Redis Queue (RQ) worker.

- Idempotency
  Duplicate webhooks for the same transaction_id are ignored.

- Persistent Storage
  Processed transactions are stored in a managed PostgreSQL database.


------------------------------------------------------------
ARCHITECTURE OVERVIEW
------------------------------------------------------------
External Payment Processor (Razorpay)
   |
   v
FastAPI App (Webhook API) --> Redis Queue --> RQ Worker --> PostgreSQL DB


------------------------------------------------------------
TECH STACK
------------------------------------------------------------
API Framework: FastAPI
Background Jobs: Redis + RQ (Redis Queue)
Database: PostgreSQL (Railway managed)
Deployment: Railway.app (managed hosting, Postgres + Redis)
Language: Python 3.11


------------------------------------------------------------
LOCAL SETUP INSTRUCTIONS
------------------------------------------------------------

1. Clone Repository
   git clone https://github.com/<your-username>/Assessment_Backend_WalnutFolks.git
   cd Assessment_Backend_WalnutFolks

2. Create Virtual Environment
   python -m venv .venv
   source .venv/bin/activate   (on Windows: .venv\Scripts\activate)
   pip install -r requirements.txt

3. Set Up Environment Variables
   Create a .env file in the project root with:

   DATABASE_URL=postgresql://postgres:<password>@localhost:5432/transactions
   REDIS_URL=redis://localhost:6379
   PORT=8000

   (On Railway, these are automatically provided.)

4. Create Database Table
   python create_table.py

5. Start the Web API
   uvicorn app.main:app --host 0.0.0.0 --port 8000

6. Start the Background Worker
   rq worker default --url $REDIS_URL


------------------------------------------------------------
TESTING THE SERVICE
------------------------------------------------------------

1. Health Check
   curl https://assessmentbackendwalnutfolks-production.up.railway.app/

   Response:
   {
     "status": "HEALTHY",
     "current_time": "2025-10-29T12:00:00Z"
   }

2. Send Webhook
   curl -X POST "https://assessmentbackendwalnutfolks-production.up.railway.app/v1/webhooks/transactions" -H "Content-Type: application/json" -d "{\"transaction_id\":\"txn_test_001\",\"source_account\":\"acc_user_001\",\"destination_account\":\"acc_merchant_001\",\"amount\":1500,\"currency\":\"INR\"}"


   Response:
   {}

   (This means the webhook was accepted and is being processed in the background.)

3. Check Transaction Status
   curl -X GET https://assessmentbackendwalnutfolks-production.up.railway.app/v1/transactions/txn_test_001

   Response (after ~30 seconds):
   {
     "transaction_id": "txn_test_001",
     "source_account": "acc_user_001",
     "destination_account": "acc_merchant_001",
     "amount": 1500,
     "currency": "INR",
     "status": "PROCESSED",
     "created_at": "2025-10-29T12:00:00Z",
     "processed_at": "2025-10-29T12:00:30Z"
   }


------------------------------------------------------------
DEPLOYMENT ON RAILWAY
------------------------------------------------------------

1. Create a new Railway project.
2. Add services:
   - Web Service (FastAPI app)
   - Redis (for job queue)
   - Postgres (for storage)
3. Add Environment Variables:
   DATABASE_URL=<Railway internal Postgres URL>
   REDIS_URL=<Railway internal Redis URL>
   PORT=8000

4. Deploy Web Service with:
   uvicorn app.main:app --host 0.0.0.0 --port 8000

5. Deploy Worker Service with:
   rq worker default --url $REDIS_URL

Once both are running, the webhook and background processing pipeline are live.


------------------------------------------------------------
EXAMPLE TEST RESULTS
------------------------------------------------------------
Test                     | Input                     | Expected Behavior
--------------------------|---------------------------|------------------------
Single Webhook            | 1 webhook                 | Processed after ~30s
Duplicate Webhook         | Same transaction_id twice | Only one record processed
Performance               | Parallel webhooks         | Responds under 500ms
Reliability               | Worker restart            | No transactions lost


------------------------------------------------------------
TECHNICAL CHOICES (EXPLANATION)
------------------------------------------------------------
- FastAPI: Chosen for async support and performance. Allows quick response without blocking.
- Redis + RQ: Reliable, simple background job system ensuring retries and idempotency.
- PostgreSQL: Strong consistency, timestamps, and unique constraints.
- Railway: Simplifies deployment with managed services for Redis and Postgres.
- Docker: Provides consistent environment locally and in production.


------------------------------------------------------------
SUMMARY
------------------------------------------------------------
Response time under 500 ms - Achieved
Duplicate prevention - Implemented
Background reliability - Ensured via Redis Queue
Cloud deployment - Live on Railway

Production API Endpoint:
https://assessmentbackendwalnutfolks-production.up.railway.app/

------------------------------------------------------------
AUTHOR
------------------------------------------------------------
Name: Pruthviram R
Tech Stack: FastAPI · Python · Redis (RQ) · PostgreSQL · Railway

------------------------------------------------------------
WHY THIS TECH STACK WAS USED
------------------------------------------------------------
This stack was chosen to build a reliable, scalable, and maintainable webhook processing service.
FastAPI was selected as the web framework because it is modern, lightweight, and supports asynchronous request handling — allowing the service to instantly acknowledge webhooks without blocking while maintaining high performance.
Redis and RQ (Redis Queue) were used to manage background jobs efficiently, providing fault-tolerant task execution with retry mechanisms.
PostgreSQL was chosen for its reliability, ACID compliance, and strong schema capabilities, which ensure each transaction is stored safely and uniquely.
Railway.app was used as the deployment platform because it offers managed PostgreSQL and Redis services out of the box, enabling seamless cloud deployment with minimal configuration.
Together, these technologies provide a clean separation between immediate request acknowledgment, durable background processing, and persistent data storage — resulting in a robust and production-ready webhook infrastructure.
