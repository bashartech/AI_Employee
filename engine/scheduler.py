"""
Scheduler module
Handles periodic task execution and automation scheduling
"""

import time
import threading
from typing import Callable, Dict, List, Optional
from datetime import datetime, timedelta
from engine.logger import logger


class ScheduledTask:
    def __init__(self, name: str, func: Callable, interval: int, enabled: bool = True):
        self.name = name
        self.func = func
        self.interval = interval  # seconds
        self.enabled = enabled
        self.last_run = None
        self.next_run = datetime.now()
        self.run_count = 0

    def should_run(self) -> bool:
        """Check if task should run now"""
        return self.enabled and datetime.now() >= self.next_run

    def execute(self):
        """Execute the scheduled task"""
        try:
            logger.info(f"Executing scheduled task: {self.name}")
            self.func()
            self.last_run = datetime.now()
            self.next_run = self.last_run + timedelta(seconds=self.interval)
            self.run_count += 1
            logger.info(f"Task {self.name} completed (run #{self.run_count})")

        except Exception as e:
            logger.error(f"Error executing task {self.name}: {e}")
            # Still update next run time even on error
            self.next_run = datetime.now() + timedelta(seconds=self.interval)


class Scheduler:
    def __init__(self):
        self.tasks: Dict[str, ScheduledTask] = {}
        self.running = False
        self.thread: Optional[threading.Thread] = None

        logger.info("Scheduler initialized")

    def add_task(self, name: str, func: Callable, interval: int, enabled: bool = True):
        """
        Add a scheduled task

        Args:
            name: Unique task name
            func: Function to execute
            interval: Interval in seconds
            enabled: Whether task is enabled
        """
        task = ScheduledTask(name, func, interval, enabled)
        self.tasks[name] = task
        logger.info(f"Added scheduled task: {name} (interval: {interval}s)")

    def remove_task(self, name: str):
        """Remove a scheduled task"""
        if name in self.tasks:
            del self.tasks[name]
            logger.info(f"Removed scheduled task: {name}")

    def enable_task(self, name: str):
        """Enable a scheduled task"""
        if name in self.tasks:
            self.tasks[name].enabled = True
            logger.info(f"Enabled task: {name}")

    def disable_task(self, name: str):
        """Disable a scheduled task"""
        if name in self.tasks:
            self.tasks[name].enabled = False
            logger.info(f"Disabled task: {name}")

    def start(self):
        """Start the scheduler"""
        if self.running:
            logger.warning("Scheduler already running")
            return

        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info("Scheduler started")

    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Scheduler stopped")

    def _run_loop(self):
        """Main scheduler loop"""
        logger.info("Scheduler loop started")

        while self.running:
            try:
                # Check all tasks
                for task in self.tasks.values():
                    if task.should_run():
                        task.execute()

                # Sleep briefly to avoid busy waiting
                time.sleep(1)

            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(5)

    def get_status(self) -> List[Dict[str, any]]:
        """Get status of all scheduled tasks"""
        status = []

        for task in self.tasks.values():
            status.append({
                'name': task.name,
                'enabled': task.enabled,
                'interval': task.interval,
                'last_run': task.last_run.isoformat() if task.last_run else None,
                'next_run': task.next_run.isoformat(),
                'run_count': task.run_count
            })

        return status

    def run_task_now(self, name: str):
        """Manually trigger a task to run immediately"""
        if name in self.tasks:
            logger.info(f"Manually triggering task: {name}")
            self.tasks[name].execute()
        else:
            logger.warning(f"Task not found: {name}")


# Predefined schedule presets
SCHEDULE_PRESETS = {
    'every_minute': 60,
    'every_5_minutes': 300,
    'every_15_minutes': 900,
    'every_30_minutes': 1800,
    'hourly': 3600,
    'every_2_hours': 7200,
    'every_6_hours': 21600,
    'daily': 86400
}


def create_scheduler_with_defaults() -> Scheduler:
    """Create a scheduler with common default tasks"""
    scheduler = Scheduler()

    # Example default tasks (to be customized)
    # scheduler.add_task('check_inbox', check_inbox_func, SCHEDULE_PRESETS['every_minute'])
    # scheduler.add_task('process_tasks', process_tasks_func, SCHEDULE_PRESETS['every_5_minutes'])
    # scheduler.add_task('cleanup', cleanup_func, SCHEDULE_PRESETS['daily'])

    return scheduler
