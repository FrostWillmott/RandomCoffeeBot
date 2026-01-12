"""Trigger script for manually testing scheduler functions.

This script allows running scheduler tasks manually without modifying
the scheduler intervals in app/scheduler.py.

Usage (local):
    uv run python -m scripts.test_run create_session
    uv run python -m scripts.test_run close_registrations
    uv run python -m scripts.test_run run_matching
    uv run python -m scripts.test_run all

Usage (Docker):
    docker compose exec bot python -m scripts.test_run create_session
    docker compose exec bot python -m scripts.test_run close_registrations
    docker compose exec bot python -m scripts.test_run run_matching
    docker compose exec bot python -m scripts.test_run all
"""

import argparse
import asyncio
import logging
import sys
from typing import Literal

from app.bot import get_bot
from app.config import get_settings
from app.db.session import engine
from app.scheduler import create_and_announce_session
from app.services.matching import (
    close_registration_for_expired_sessions,
    run_matching_for_closed_sessions,
)
from app.utils.logging import setup_logging


async def run_create_session(bot) -> None:
    """Run the create_and_announce_session task."""
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("Running: create_and_announce_session")
    logger.info("=" * 60)
    try:
        await create_and_announce_session(bot)
        logger.info("✓ create_and_announce_session completed successfully")
    except Exception as e:  # Catch all unexpected errors for logging in a test script
        logger.exception("✗ create_and_announce_session failed", exc_info=e)
        raise


async def run_close_registrations() -> None:
    """Run the close_registration_for_expired_sessions task."""
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("Running: close_registration_for_expired_sessions")
    logger.info("=" * 60)
    try:
        await close_registration_for_expired_sessions()
        logger.info("✓ close_registration_for_expired_sessions completed successfully")
    except Exception as e:  # Catch all unexpected errors for logging in a test script
        logger.exception("✗ close_registration_for_expired_sessions failed", exc_info=e)
        raise


async def run_matching(bot) -> None:
    """Run run_matching_for_closed_sessions task."""
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("Running: run_matching_for_closed_sessions")
    logger.info("=" * 60)
    try:
        await run_matching_for_closed_sessions(bot)
        logger.info("✓ run_matching_for_closed_sessions completed successfully")
    except Exception as e:  # Catch all unexpected errors for logging in a test script
        logger.exception("✗ run_matching_for_closed_sessions failed", exc_info=e)
        raise


async def run_all(bot) -> None:
    """Run all scheduler tasks in sequence."""
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("Running all scheduler tasks")
    logger.info("=" * 60)

    tasks = [
        ("create_session", lambda: run_create_session(bot)),
        ("close_registrations", run_close_registrations),
        ("run_matching", lambda: run_matching(bot)),
    ]

    for task_name, task_func in tasks:
        try:
            logger.info(f"\n>>> Starting task: {task_name}")
            await task_func()
            logger.info(f"<<< Completed task: {task_name}\n")
        except Exception:  # Catch all unexpected errors for logging in a test script
            logger.error(f"Task {task_name} failed, stopping execution")
            raise


async def main_async(
    action: Literal["create_session", "close_registrations", "run_matching", "all"],
) -> None:
    """Main async function to run the selected action."""
    logger = logging.getLogger(__name__)
    bot = None

    try:
        logger.info("Initializing bot and database connections...")
        bot = await get_bot()

        if action == "create_session":
            await run_create_session(bot)
        elif action == "close_registrations":
            await run_close_registrations()
        elif action == "run_matching":
            await run_matching(bot)
        elif action == "all":
            await run_all(bot)
        else:
            logger.error(f"Unknown action: {action}")
            sys.exit(1)

        logger.info("=" * 60)
        logger.info("All tasks completed successfully!")
        logger.info("=" * 60)

    except Exception as e:  # Catch all unexpected errors for logging in a test script
        logger.exception("Script execution failed", exc_info=e)
        sys.exit(1)
    finally:
        # Cleanup resources
        if bot:
            try:
                await bot.session.close()
            except Exception as e:  # Catch all unexpected errors for logging
                logger.warning(f"Error closing bot session: {e}")

        try:
            await engine.dispose()
        except Exception as e:  # Catch all unexpected errors for logging in a test script
            logger.warning(f"Error disposing database engine: {e}")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Trigger scheduler functions manually for testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Local:
  uv run python -m scripts.test_run create_session
  uv run python -m scripts.test_run close_registrations
  uv run python -m scripts.test_run run_matching
  uv run python -m scripts.test_run all

  # Docker:
  docker compose exec bot python -m scripts.test_run create_session
  docker compose exec bot python -m scripts.test_run all
        """,
    )

    parser.add_argument(
        "action",
        choices=["create_session", "close_registrations", "run_matching", "all"],
        help="Action to perform",
    )

    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)",
    )

    parser.add_argument(
        "--log-format",
        default="text",
        choices=["text", "json"],
        help="Log format (default: text)",
    )

    args = parser.parse_args()

    settings = get_settings()
    log_level = args.log_level or settings.log_level
    log_format = args.log_format or settings.log_format
    setup_logging(log_level, log_format)

    asyncio.run(main_async(args.action))


if __name__ == "__main__":
    main()
