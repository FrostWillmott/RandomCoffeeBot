"""Tests for scheduler configuration."""

from apscheduler.triggers.cron import CronTrigger

from app.scheduler import setup_scheduler


def test_scheduler_initialization(bot):
    """Test that scheduler can be initialized with valid configuration."""
    scheduler = setup_scheduler(bot)

    assert scheduler is not None
    jobs = scheduler.get_jobs()
    assert len(jobs) == 3

    job_ids = {job.id for job in jobs}
    assert "create_weekly_session" in job_ids
    assert "close_registrations" in job_ids
    assert "run_matching" in job_ids


def test_scheduler_cron_trigger_configuration(bot):
    """Test that all CronTrigger configurations are valid."""
    scheduler = setup_scheduler(bot)

    for job in scheduler.get_jobs():
        assert isinstance(job.trigger, CronTrigger), f"Job {job.id} should use CronTrigger"

        # Verify trigger can be converted to string (validates internal structure)
        trigger_str = str(job.trigger)
        assert "cron" in trigger_str.lower(), f"Job {job.id} should have cron trigger"

        # Verify specific configurations by checking trigger string representation
        if job.id == "create_weekly_session":
            assert "mon" in trigger_str or "day_of_week='mon'" in trigger_str
            assert "hour='10'" in trigger_str or "hour=10" in trigger_str
            assert "minute='0'" in trigger_str or "minute=0" in trigger_str
        elif job.id == "close_registrations":
            assert "minute='0'" in trigger_str or "minute=0" in trigger_str
        elif job.id == "run_matching":
            assert "minute='15'" in trigger_str or "minute=15" in trigger_str


def test_scheduler_job_arguments(bot):
    """Test that jobs have correct arguments."""
    scheduler = setup_scheduler(bot)

    create_session_job = next(
        j for j in scheduler.get_jobs() if j.id == "create_weekly_session"
    )
    assert create_session_job.args == (bot,)

    run_matching_job = next(j for j in scheduler.get_jobs() if j.id == "run_matching")
    assert run_matching_job.args == (bot,)

    close_registrations_job = next(
        j for j in scheduler.get_jobs() if j.id == "close_registrations"
    )
    assert close_registrations_job.args == ()
