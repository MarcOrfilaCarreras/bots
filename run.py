import time

import schedule

from bots.core import logger
from bots.menorca_properties import run as run_menorca_properties
from bots.subastas_boe import run as run_subastas_boe


def main() -> None:
    """
    The main entry point for the application.
    """

    logger.info('Application started. Scheduler is now running.')

    schedule.every().day.at('18:00').do(run_subastas_boe)
    schedule.every().day.at('20:00').do(run_menorca_properties)

    while True:
        schedule.run_pending()
        time.sleep(1 * 60)


if __name__ == '__main__':
    main()
