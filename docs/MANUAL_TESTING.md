# Random Coffee Bot Testing Guide

This guide will help you verify the bot's functionality and ensure that all features are working correctly.

## Section 1: Preparation

### 1.1 Configuration Check

Ensure your `.env` file is configured correctly:

```bash
# Check for mandatory variables:
TELEGRAM_BOT_TOKEN=your_bot_token_here
CHANNEL_ID=@your_channel_username
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/randomcoffee
REDIS_URL=redis://redis:6379/0
```

**Important:**
- `TELEGRAM_BOT_TOKEN` must be obtained from [@BotFather](https://t.me/BotFather)
- `CHANNEL_ID` should be the ID or username of the channel where announcements will be posted
- For local runs, change `DATABASE_URL` to `postgresql+asyncpg://postgres:postgres@localhost:5432/randomcoffee`

### 1.2 Database Migrations Check

Ensure all migrations are applied:

```bash
# In Docker:
make migrate

# Locally:
alembic upgrade head
```

### 1.3 Discussion Topics Check

Discussion topics should be loaded into the database. Check and load them if necessary:

```bash
# In Docker:
make db-seed

# Locally:
uv run python scripts/seed_topics.py
```

The script will automatically check for existing topics and load them if the database is empty.

**Verification via SQL (optional):**

```bash
# Connect to the database:
make db-shell

# Run the query:
SELECT COUNT(*) FROM topics WHERE is_active = true;
SELECT category, COUNT(*) FROM topics GROUP BY category;
```

Dozens of topics should be loaded across various categories (core_python, frameworks, architecture, etc.).

## Section 2: Running the Bot

### 2.1 Running in Docker (Recommended)

```bash
# Start all services (bot, db, redis):
make dev

# Check container status:
make ps

# View logs:
make logs

# Or only bot logs:
docker compose logs -f bot
```

**Successful Startup Verification:**

1. The logs should show a message indicating the bot has started:
   ```
   Bot started successfully
   Scheduler started
   ```

2. Containers should be in the `Up` status:
   ```bash
   make ps
   ```

3. Check the heartbeat file (if configured):
   ```bash
   docker compose exec bot cat /tmp/healthy
   ```

### 2.2 Running Locally (Without Docker)

**Requirements:**
- PostgreSQL running at localhost:5432
- Redis running at localhost:6379
- `DATABASE_URL` in `.env` changed to `postgresql+asyncpg://postgres:postgres@localhost:5432/randomcoffee`

```bash
# Start the bot:
make run

# Or directly:
uv run python -m app.main
```

**Successful Startup Verification:**

The console should display the following messages:
```
INFO: Bot started successfully
INFO: Scheduler started
INFO: Polling started
```

## Section 3: Testing Core Functions

### 3.1 Testing the /start Command

1. Find your bot on Telegram (using the username you specified during creation)
2. Send the `/start` command
3. **Expected Result:**
   - The bot should respond with a welcome message
   - A main menu with buttons should appear
   - For new users: a full description of how the bot works
   - For existing users: a brief greeting

**Database Verification:**
```bash
make db-shell
SELECT * FROM users WHERE telegram_id = YOUR_TELEGRAM_ID;
```

The user should be created or updated in the database.

### 3.2 Testing the /help Command

1. Send the `/help` command to the bot
2. **Expected Result:**
   - The bot should send a message with help information
   - Information about available commands should be included
   - A description of the Random Coffee process should be present

### 3.3 Testing the /status Command

1. Send the `/status` command to the bot
2. **Expected Result:**
   - The bot should show your current status
   - Information about registrations for upcoming sessions
   - Information about current matches

### 3.4 Testing the Main Menu

1. Click the buttons in the main menu:
   - **"Registration"** - the registration form should open
   - **"My Matches"** - your current matches should be shown
   - **"Help"** - help information should be shown

### 3.5 Testing the Scheduler

The scheduler automatically performs tasks according to the schedule. For testing, tasks can be run manually:

#### 3.5.1 Session Creation

```bash
# In Docker:
docker compose exec bot python -m scripts.test_run create_session

# Locally:
uv run python -m scripts.test_run create_session
```

**Expected Result:**
- The logs should show a message about the session creation
- An announcement message should appear in the channel (specified in `CHANNEL_ID`)
- A new session should be created in the database:
  ```bash
  make db-shell
  SELECT * FROM sessions ORDER BY created_at DESC LIMIT 1;
  ```

**Important:** If a session for the current week already exists with a different status (CLOSED, MATCHED, COMPLETED), the command will output a warning and will NOT create a new announcement. To re-test, use the `reset` command (see Section 3.5.5).

#### 3.5.2 Closing Registrations

**Important:** Closing registrations only works for sessions with an expired deadline (`registration_deadline < NOW()`). For testing, you must first set a past deadline:

```bash
# Set deadline to a past date (replace SESSION_ID with your session's ID)
docker compose exec -T db psql -U randomcoffee -d randomcoffee -c "UPDATE sessions SET registration_deadline = NOW() - INTERVAL '1 day' WHERE id = SESSION_ID;"

# Then run the registration closing
# In Docker:
docker compose exec bot python -m scripts.test_run close_registrations

# Locally:
uv run python -m scripts.test_run close_registrations
```

**Expected Result:**
- Sessions with expired registration deadlines should be closed
- The session status should change to `CLOSED`

#### 3.5.3 Running Matching

**Important:** Matching only works for sessions with status `CLOSED` and an expired registration deadline. If a session is still open, matching will not find any sessions to process.

**Preparing a Session for Matching:**

Before running the matching process, ensure the session is closed. There are two ways:

**Method 1: Automatic Closing (Recommended for Testing)**
```bash
# Set deadline to a past date
docker compose exec -T db psql -U randomcoffee -d randomcoffee -c "UPDATE sessions SET registration_deadline = NOW() - INTERVAL '1 day' WHERE id = SESSION_ID;"

# Close registrations (will automatically close the session)
docker compose exec bot python -m scripts.test_run close_registrations
```

**Method 2: Manual Closing**
```bash
# IMPORTANT: When closing manually, you also need to set a past deadline,
# otherwise matching won't find the session (requires: status = 'closed' AND registration_deadline < NOW())

# Set a past deadline
docker compose exec -T db psql -U randomcoffee -d randomcoffee -c "UPDATE sessions SET registration_deadline = NOW() - INTERVAL '1 day' WHERE id = SESSION_ID;"

# Manually close the session
docker compose exec -T db psql -U randomcoffee -d randomcoffee -c "UPDATE sessions SET status = 'closed' WHERE id = SESSION_ID;"
```

**Running Matching:**
```bash
# In Docker:
docker compose exec bot python -m scripts.test_run run_matching

# Locally:
uv run python -m scripts.test_run run_matching
```

**Expected Result:**
- Matches should be created for closed sessions
- Participants should receive match notifications in the channel and private messages
- Records should be created in the `matches` table in the database

**Database Verification:**
```bash
make db-shell
SELECT * FROM matches ORDER BY created_at DESC LIMIT 5;
SELECT * FROM registrations WHERE session_id = SESSION_ID;
SELECT id, status, registration_deadline FROM sessions WHERE id = SESSION_ID;
```

**If matching does not find sessions:**
- Ensure the session status is `CLOSED`
- **CRITICAL:** Check that `registration_deadline < NOW()` - matching requires BOTH conditions:
  - `status = 'closed'` AND
  - `registration_deadline < current_time`
- If the deadline is in the future, set it to a past date:
  ```bash
  docker compose exec -T db psql -U randomcoffee -d randomcoffee -c "UPDATE sessions SET registration_deadline = NOW() - INTERVAL '1 day' WHERE id = SESSION_ID;"
  ```
- Check for registrations for the session (minimum 2 users for a pair, 3 for a triplet)

#### 3.5.4 Running All Tasks

**Important:** The `all` command executes all three tasks sequentially, but it is **not suitable** for real testing without prior preparation. Reason: after creating a session, the deadline will be in the future, so `close_registrations` and `run_matching` will find nothing.

**When to use `all`:**
- Only if you have previously changed the deadline of an existing session to a past date
- Or to verify that all commands execute without errors (though no real work will be done)

```bash
# In Docker:
docker compose exec bot python -m scripts.test_run all

# Locally:
uv run python -m scripts.test_run all
```

**For full cycle testing, use Section 3.6 "Full Cycle Testing".**

#### 3.5.5 Resetting Data for Repeated Testing

After completing a full testing cycle (creation → registration → closing → matching), the session transitions to `MATCHED` status. To repeat the test, you need to delete the current session:

```bash
# In Docker:
docker compose exec bot python -m scripts.test_run reset

# Locally:
uv run python -m scripts.test_run reset
```

**What the `reset` command does:**
- Finds the last session in the database
- Deletes all matches for this session
- Deletes all registrations for this session
- Deletes the session itself

**When to use:**
- After completing a full testing cycle
- If a session is in the wrong status
- Before re-testing from a clean state

**Typical Repeat Testing Cycle:**
```bash
# 1. Reset previous data
docker compose exec bot python -m scripts.test_run reset

# 2. Create a new session
docker compose exec bot python -m scripts.test_run create_session

# 3. Register via reaction in the channel
# ... (put 👍 on the announcement)

# 4. Get the ID of the created session
docker compose exec -T db psql -U randomcoffee -d randomcoffee -c "SELECT id FROM sessions ORDER BY created_at DESC LIMIT 1;"

# 5. Set a past deadline (replace SESSION_ID with the obtained ID)
docker compose exec -T db psql -U randomcoffee -d randomcoffee -c "UPDATE sessions SET registration_deadline = NOW() - INTERVAL '1 day' WHERE id = SESSION_ID;"

# 6. Close registrations and run matching
docker compose exec bot python -m scripts.test_run close_registrations
docker compose exec bot python -m scripts.test_run run_matching
```

### 3.6 Full Cycle Testing

1. **Create a test session:**
   ```bash
   docker compose exec bot python -m scripts.test_run create_session
   ```

2. **Register via the bot:**
   - Open the channel where the announcement was published
   - React with 👍 to the announcement message
   - Or use the registration command in the bot

3. **Verify registration:**
   ```bash
   make db-shell
   # Find registrations by telegram_id (replace YOUR_TELEGRAM_ID with your ID)
   SELECT r.* FROM registrations r
   JOIN users u ON r.user_id = u.id
   WHERE u.telegram_id = YOUR_TELEGRAM_ID;
   ```

4. **Get the ID of the created session:**
   ```bash
   docker compose exec -T db psql -U randomcoffee -d randomcoffee -c "SELECT id FROM sessions ORDER BY created_at DESC LIMIT 1;"
   ```

5. **Prepare the session for matching** (replace SESSION_ID with the obtained ID):

   **Option A: Automatic Closing (Recommended)**
   ```bash
   # Set deadline to a past date
   docker compose exec -T db psql -U randomcoffee -d randomcoffee -c "UPDATE sessions SET registration_deadline = NOW() - INTERVAL '1 day' WHERE id = SESSION_ID;"

   # Close registrations (will automatically close the session)
   docker compose exec bot python -m scripts.test_run close_registrations
   ```

   **Option B: Manual Closing**
   ```bash
   # IMPORTANT: Manual closing also requires setting a past deadline,
   # otherwise matching will not find the session

   # Set a past deadline
   docker compose exec -T db psql -U randomcoffee -d randomcoffee -c "UPDATE sessions SET registration_deadline = NOW() - INTERVAL '1 day' WHERE id = SESSION_ID;"

   # Manually close the session
   docker compose exec -T db psql -U randomcoffee -d randomcoffee -c "UPDATE sessions SET status = 'closed' WHERE id = SESSION_ID;"
   ```

6. **Run matching:**
   ```bash
   docker compose exec bot python -m scripts.test_run run_matching
   ```

7. **Verify the result:**
   - An announcement message with a list of all matches should appear in the channel
   - You should receive a private match notification
   - A match with a discussion topic should be created in the database
   ```bash
   make db-shell
   SELECT m.id, u1.username as user1, u2.username as user2, t.title as topic
   FROM matches m
   JOIN users u1 ON m.user1_id = u1.id
   JOIN users u2 ON m.user2_id = u2.id
   LEFT JOIN topics t ON m.topic_id = t.id
   WHERE m.session_id = SESSION_ID;
   ```

## Section 4: Health Checks

### 4.1 Database Connection Check

```bash
# Check connection via psql:
make db-shell

# Or check via Python:
docker compose exec bot python -c "
from app.db.session import engine
import asyncio
async def check():
    async with engine.connect() as conn:
        result = await conn.execute('SELECT 1')
        print('Database connection: OK')
asyncio.run(check())
"
```

**Expected Result:** Connection successful, query executes.

### 4.2 Telegram API Connection Check

```bash
# Check via logs:
make logs | grep -i "telegram\|bot started"

# Or check bot status:
docker compose exec bot python -c "
from app.bot import get_bot
import asyncio
async def check():
    bot = await get_bot()
    me = await bot.get_me()
    print(f'Bot connected: {me.username} (@{me.username})')
    await bot.session.close()
asyncio.run(check())
"
```

**Expected Result:** Bot successfully connected, information about the bot is returned.

### 4.3 Redis Check

```bash
# Check Redis connection:
docker compose exec redis redis-cli ping

# Should return: PONG
```

### 4.4 Checking Logs for Errors

```bash
# View logs:
make logs

# Or only errors:
make logs | grep -i "error\|exception\|failed"

# Check bot logs:
docker compose logs bot | tail -50
```

**What to check:**
- No critical errors (ERROR, CRITICAL)
- No exceptions (Exception, Traceback)
- No problems connecting to the database or Telegram API

## Section 5: Common Issues and Solutions

### 5.1 Bot Does Not Respond to Commands

**Possible Reasons:**
1. Bot is not running - check `make ps` or logs
2. Incorrect `TELEGRAM_BOT_TOKEN` - check your `.env` file
3. Bot is blocked by the user - unblock the bot on Telegram

**Solution:**
```bash
# Check status:
make ps

# Restart:
make down
make dev

# Check logs:
make logs
```

### 5.2 Database Connection Errors

**Possible Reasons:**
1. Database is not running
2. Incorrect `DATABASE_URL` in `.env`
3. Migrations have not been applied

**Solution:**
```bash
# Check DB status:
docker compose ps db

# Check connection:
make db-shell

# Apply migrations:
make migrate

# Restart DB:
docker compose restart db
```

### 5.3 Missing Topics in the Database

**Symptoms:**
- No available topics during matching
- In logs: "No topics available for matching!"

**Solution:**
```bash
# Load topics:
make db-seed

# Check count:
make db-shell
SELECT COUNT(*) FROM topics WHERE is_active = true;
```

### 5.4 Configuration Issues

**Symptoms:**
- Errors during bot startup
- Messages about missing environment variables

**Solution:**
1. Check for the existence of the `.env` file
2. Ensure all mandatory variables are set:
   - `TELEGRAM_BOT_TOKEN`
   - `CHANNEL_ID`
   - `DATABASE_URL`
   - `REDIS_URL`
3. Check the format of the values (no extra spaces, quotes)
4. Restart the bot after changing `.env`:
   ```bash
   make down
   make dev
   ```

### 5.5 Scheduler Does Not Execute Tasks

**Symptoms:**
- Sessions are not created automatically
- Registrations are not closed
- Matching is not initiated

**Solution:**
1. Check scheduler logs:
   ```bash
   make logs | grep -i "scheduler\|job"
   ```

2. Run tasks manually for verification:
   ```bash
   docker compose exec bot python -m scripts.test_run all
   ```

3. Check scheduler settings in `app/scheduler.py` and `app/constants.py`

### 5.6 Matching Does Not Find Sessions to Process

**Symptoms:**
- `run_matching` command finishes without errors but reports "0 sessions"
- In logs: "Closed registration for 0 sessions" or "Found 0 closed sessions ready for matching"

**Possible Reasons:**
1. Session is still open (status `open` instead of `closed`)
2. Registration deadline has not yet expired
3. No registrations for the session

**Solution:**
1. Check session status:
   ```bash
   make db-shell
   SELECT id, status, registration_deadline, NOW() as current_time FROM sessions WHERE id = SESSION_ID;
   ```

2. If the session is open, close it:
   ```bash
   # Set a past deadline and close automatically
   docker compose exec -T db psql -U randomcoffee -d randomcoffee -c "UPDATE sessions SET registration_deadline = NOW() - INTERVAL '1 day' WHERE id = SESSION_ID;"
   docker compose exec bot python -m scripts.test_run close_registrations

   # Or close manually (IMPORTANT: also set a past deadline!)
   docker compose exec -T db psql -U randomcoffee -d randomcoffee -c "UPDATE sessions SET registration_deadline = NOW() - INTERVAL '1 day' WHERE id = SESSION_ID;"
   docker compose exec -T db psql -U randomcoffee -d randomcoffee -c "UPDATE sessions SET status = 'closed' WHERE id = SESSION_ID;"
   ```

3. Check for registrations:
   ```bash
   make db-shell
   SELECT COUNT(*) FROM registrations WHERE session_id = SESSION_ID;
   ```
   There must be at least 2 registrations to create a pair.

### 5.7 Notifications Are Not Sent

**Possible Reasons:**
1. User blocked the bot
2. Errors in the Telegram API
3. Incorrect message format

**Solution:**
1. Check logs for sending errors:
   ```bash
   make logs | grep -i "notification\|telegram\|send"
   ```

2. Verify that the user has not blocked the bot
3. Check bot permissions (must be able to send messages)

### 5.8 Registration Is for an Old Session / Announcement Is Not Published

**Symptoms:**
- A warning about status appears when creating a session
- Registration via reaction does not work
- When re-running `create_session`, the announcement is not published

**Possible Reasons:**
1. A session for the current week already exists with a status other than OPEN (CLOSED, MATCHED, COMPLETED)
2. This is a repeat test without resetting data

**Solution:**
```bash
# Reset the data of the last session
docker compose exec bot python -m scripts.test_run reset

# Create a new session
docker compose exec bot python -m scripts.test_run create_session
```

**Checking Session State:**
```bash
make db-shell
SELECT id, date, status, announcement_message_id FROM sessions ORDER BY date DESC LIMIT 5;
```

## Quick Check Checklist

Use this checklist for a quick health check:

- [ ] `.env` configuration is set up correctly
- [ ] Migrations applied (`make migrate`)
- [ ] Topics loaded into the database (`make db-seed`)
- [ ] Bot is running (`make ps`, `make logs`)
- [ ] `/start` command works and creates a user
- [ ] `/help` command returns help information
- [ ] `/status` command shows user status
- [ ] Main menu displays correctly
- [ ] Session creation works (`scripts/test_run create_session`)
- [ ] Announcement is published in the channel
- [ ] Registration via reaction works
- [ ] Session is closed before matching (status `closed`, deadline expired)
- [ ] Matching creates pairs (`scripts/test_run run_matching`)
- [ ] Match notifications are sent
- [ ] No errors in logs
- [ ] For repeat tests: data reset works (`scripts/test_run reset`)

## Additional Debugging Commands

```bash
# View all users:
make db-shell
SELECT id, telegram_id, username, first_name, is_active FROM users;

# View all sessions:
SELECT id, date, status, registration_deadline FROM sessions ORDER BY date DESC;

# View all registrations:
SELECT r.id, u.username, s.date, r.created_at
FROM registrations r
JOIN users u ON r.user_id = u.id
JOIN sessions s ON r.session_id = s.id
ORDER BY r.created_at DESC;

# View all matches:
SELECT m.id, u1.username as user1, u2.username as user2, t.title as topic, m.status
FROM matches m
JOIN users u1 ON m.user1_id = u1.id
JOIN users u2 ON m.user2_id = u2.id
LEFT JOIN topics t ON m.topic_id = t.id
ORDER BY m.created_at DESC;

# Clear test data (use with caution!):
# Delete all registrations and matches for testing:
DELETE FROM matches;
DELETE FROM registrations;
```

---

**Note:** Be careful when deleting data and running test commands in a production environment.
