import logging
import os
import time

from bi import configure_logging
from bi.scheduler import Schedular

HEARTBEAT_ = os.environ.get("SCHEDULER_HEARTBEAT_FILE", "/tmp/scheduler.heartbeat")


def main():
    """
    runs the cron jobs (dumps, scheduled queries and jobs, firewall expiry) in their own process
    and touches a heartbeat file every minute for the container health check
    """
    configure_logging()
    log_ = logging.getLogger("scheduler")
    started_ = Schedular().main_f()
    if started_ is not True:
        log_.error("scheduler failed to start: %s", started_)
        raise SystemExit(1)
    log_.info("scheduler started")
    while True:
        with open(HEARTBEAT_, "w", encoding="utf-8") as fh_:
            fh_.write(str(int(time.time())))
        time.sleep(60)


if __name__ == "__main__":
    main()
