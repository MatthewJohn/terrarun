# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0


import signal
import threading
import traceback
from time import sleep

from terrarun.database import Database
from terrarun.job_processor import JobProcessor
from terrarun.logger import get_logger
from terrarun.models.run_flow import RunStatus
from terrarun.models.state_version import StateVersion

logger = get_logger(__name__)


class Worker:
    """Provide functionality for internal worker"""

    def __init__(self):
        """Store member variables"""
        self.__running = True
        self.__job_run_subprocess = threading.Thread(target=self.check_for_jobs_loop)
        self.__state_version_subprocess = threading.Thread(target=self.check_for_state_versions_loop)

    def check_for_jobs_loop(self):
        """Enter loop to continue looking for jobs"""
        while self.__running:
            try:
                if not self._check_for_jobs():
                    sleep(5)
            except Exception:
                logger.exception('An error occured whilst checking for jobs.')
                sleep(15)

            # Clear database session to avoid cached queries
            Database.get_session().remove()

    def _check_for_jobs(self):
        """Check for jobs to run"""
        logger.debug('Checking for jobs...')
        run = JobProcessor.get_worker_job()
        if not run:
            logger.debug('No run in queue')
            return None

        logger.info('Handling run. Id: %s. Status: %s', run.api_id, run.status)

        if run.status is RunStatus.PENDING:
            run.handling_pending()

        # Check status of pre-plan tasks
        elif run.status is RunStatus.PRE_PLAN_RUNNING:
            run.handle_pre_plan_running()

        elif run.status is RunStatus.PRE_PLAN_COMPLETED:
            run.queue_plan()

        elif run.status is RunStatus.PLANNED:
            run.handle_planned()

        # Check status of post-plan tasks
        elif run.status is RunStatus.POST_PLAN_RUNNING:
            run.handle_post_plan_running()

        elif run.status is RunStatus.POST_PLAN_COMPLETED:
            run.handle_post_plan_completed()

        # Handle confirmed, starting pre-apply tasks
        elif run.status is RunStatus.CONFIRMED:
            run.handle_confirmed()

        # Check status of pre-apply tasks
        elif run.status is RunStatus.PRE_APPLY_RUNNING:
            run.handle_pre_apply_running()

        elif run.status is RunStatus.CANCELED:
            # Handle cancelled run
            run.unlock_workspace()
        else:
            logger.error('Unknown job status. Id: %s. Status: %s', run.api_id, run.status)


    def check_for_state_versions_loop(self):
        """Enter loop to continue looking for jobs"""
        while self.__running:
            try:
                if not self._check_for_state_version():
                    sleep(5)
            except Exception:
                logger.exception('An error occured whilst checking for state versions.')
                sleep(15)

            # Clear database session to avoid cached queries
            Database.get_session().remove()

    def _check_for_state_version(self):
        """Check for unprocessed state versions to process"""
        logger.debug('Checking for unprocessed state version...')
        state_version = StateVersion.get_state_version_to_process()
        if not state_version:
            logger.debug('No unprocessed state versions')
            return None

        logger.info('Handling state version: %s', state_version.api_id)
        # Process state resources
        state_version.process_resources()

    def wait_for_jobs(self):
        """Wait for any running jobs to complete"""
        self.__job_run_subprocess.join()
        self.__state_version_subprocess.join()

    def start(self):
        """Start threads for agent"""
        signal.signal(signal.SIGINT, self.stop)
        #signal.pause()
        self.__job_run_subprocess.start()
        self.__state_version_subprocess.start()

    def stop(self, *args):
        """Stop agent"""
        logger.info('Stopping worker... waiting for remaining jobs to complete.')
        self.__running = False
        self.wait_for_jobs()
