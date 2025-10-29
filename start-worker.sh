#!/usr/bin/env bash
set -e
export REDIS_URL=${REDIS_URL:-redis://redis:6379/0}
# Start an RQ worker for the "transactions" queue
# RQ worker will import app.worker and use functions there
rq worker transactions --url $REDIS_URL