# Manual Testing

A smoke check of the bot against a real Telegram bot and channel. For the
automated suite, see [TESTING.md](TESTING.md).

## Setup

```bash
cp .env.example .env   # set TELEGRAM_BOT_TOKEN, CHANNEL_ID, POSTGRES_USER
make dev               # bot + db + redis
make migrate
make db-seed           # discussion topics; matching has nothing to assign without them
make logs              # expect "Bot started successfully" and "Scheduler started"
```

The bot must be an admin of `CHANNEL_ID` to post announcements.

## Bot commands

| Action | Expected |
|---|---|
| `/start` | Welcome text and main menu; a row appears in `users` |
| `/help` | Commands and how Random Coffee works |
| `/status` | Your registrations and current matches |
| Menu buttons | Registration, My Matches and Help each respond |

## Full cycle

Scheduler jobs can be triggered by hand with `scripts/test_run`:

```bash
docker compose exec bot python -m scripts.test_run <action>
# actions: create_session | close_registrations | run_matching | all | reset
```

1. `reset`, then `create_session` — an announcement appears in the channel.
2. React 👍 to it from at least two accounts (three to get a triplet).
3. Move the deadline into the past, because closing and matching only pick up
   sessions with `registration_deadline < NOW()`:
   ```sql
   -- make db-shell
   UPDATE sessions SET registration_deadline = NOW() - INTERVAL '1 day'
   WHERE id = (SELECT id FROM sessions ORDER BY created_at DESC LIMIT 1);
   ```
4. `close_registrations` — the session becomes `CLOSED`.
5. `run_matching` — a match list is posted to the channel, each participant
   gets a DM with their partner and topic, and rows appear in `matches`.

`all` runs `create_session`, `close_registrations` and `run_matching` back to
back, but a freshly created session has a
future deadline, so it only proves the commands run without errors.

## When something is off

| Symptom | Check |
|---|---|
| Bot is silent | `make ps`, `make logs`, `TELEGRAM_BOT_TOKEN` |
| `create_session` warns and posts nothing | A session for this week already exists in another status — run `reset` |
| Matching reports 0 sessions | Status must be `CLOSED` **and** deadline in the past; at least 2 registrations |
| "No topics available for matching!" | `make db-seed` |
| No DMs | The user hasn't started the bot or blocked it; grep logs for `notification` |

Don't run `reset` against production: it deletes the latest session together
with its registrations and matches.
