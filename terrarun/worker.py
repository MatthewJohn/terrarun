
import threading
import signal
from time import sleep
import traceback
from terrarun.database import Database
from terrarun.job_processor import JobProcessor
from terrarun.models.run import RunStatus

from terrarun.models.run_queue import RunQueue, JobQueueAgentType
from terrarun.models.state_version import StateVersion


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
            except Exception as exc:
                print('An error occured whilst processing job')
                print(exc)
                traceback.print_exception(type(exc), exc, exc.__traceback__)
                sleep(15)

            # Clear database session to avoid cached queries
            Database.get_session().remove()

    def _check_for_jobs(self):
        """Check for jobs to run"""
        print('Checking for jobs...')
        run = JobProcessor.get_worker_job()
        if not run:
            print('No run in queue')
            return None

        print(f'Handling run: {run.api_id}: {run.status}')

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

        else:
            print(f'Unknown job status for worker: {run.status}')


    def check_for_state_versions_loop(self):
        """Enter loop to continue looking for jobs"""
        while self.__running:
            try:
                if not self._check_for_state_version():
                    sleep(5)
            except Exception as exc:
                print('An error occured whilst processing job')
                print(exc)
                traceback.print_exception(type(exc), exc, exc.__traceback__)
                sleep(15)

            # Clear database session to avoid cached queries
            Database.get_session().remove()

    def _check_for_state_version(self):
        """Check for unprocessed state versions to process"""
        print('Checking for unprocessed state version...')
        state_version = StateVersion.get_state_version_to_process()
        if not state_version:
            print('No unprocessed state versions')
            return None

        print(f'Handling state version: {state_version.api_id}')
        # Process state resources
        state_version.process_resources()

    def stop(self):
        """Mark as stopped, stopping any further jobs from executing"""
        self.__running = False

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
        print('Stopping worker... waiting for remaining jobs to complete.')
        self.__running = False
        self.wait_for_jobs()
