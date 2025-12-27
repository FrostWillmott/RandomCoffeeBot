#!/bin/bash
set -e

# Wait for database to be ready with timeout
MAX_RETRIES=30
RETRY_COUNT=0

echo "Waiting for PostgreSQL..."
while ! python -c "
import asyncio
import asyncpg
import os

async def check():
    try:
        url = os.environ.get('DATABASE_URL', '').replace('+asyncpg', '')
        if not url:
            return False
        conn = await asyncpg.connect(url)
        await conn.close()
        return True
    except Exception:
        return False

exit(0 if asyncio.run(check()) else 1)
"; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "ERROR: PostgreSQL not available after $MAX_RETRIES attempts"
        exit 1
    fi
    echo "PostgreSQL is unavailable - sleeping (attempt $RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done
echo "PostgreSQL is ready!"

# Run database migrations
if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Running database migrations..."
    alembic upgrade head
fi

# Execute the main command
exec "$@"
