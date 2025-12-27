#!/bin/bash
set -e

# Wait for database to be ready
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
" 2>/dev/null; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 2
done
echo "PostgreSQL is ready!"

# Wait for Redis to be ready
echo "Waiting for Redis..."
while ! python -c "
import redis
import os
url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
r = redis.from_url(url)
r.ping()
" 2>/dev/null; do
    echo "Redis is unavailable - sleeping"
    sleep 2
done
echo "Redis is ready!"

# Run database migrations
if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Running database migrations..."
    alembic upgrade head
fi

# Execute the main command
exec "$@"
