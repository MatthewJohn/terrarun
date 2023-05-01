
import threading
import signal
from time import sleep
import traceback
from terrarun.database import Database
from terrarun.models.run import RunStatus

from terrarun.models.run_queue import RunQueue, RunQueueType


class Worker:
    """Provide functionality for internal worker"""

    def __init__(self):
        """Store member variables"""
        self.__running = True
        self.__job_run_subprocess = threading.Thread(target=self.check_for_jobs_loop)

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
        run_queue_job = RunQueue.get_job_by_type(RunQueueType.WORKER)
        if not run_queue_job:
            print('No jobs available')
            return None

        print(f'Handling run: {run_queue_job.run.api_id}: {run_queue_job.run.status}')

        if run_queue_job.run.status is RunStatus.PENDING:
            run_queue_job.run.handling_pending()

        # Check status of pre-plan tasks
        elif run_queue_job.run.status is RunStatus.PRE_PLAN_RUNNING:
            run_queue_job.run.handle_pre_plan_running()

        elif run_queue_job.run.status is RunStatus.PRE_PLAN_COMPLETED:
            run_queue_job.run.queue_plan()

        elif run_queue_job.run.status is RunStatus.PLANNED:
            run_queue_job.run.handle_planned()

        # Check status of post-plan tasks
        elif run_queue_job.run.status is RunStatus.POST_PLAN_RUNNING:
            run_queue_job.run.handle_post_plan_running()

        elif run_queue_job.run.status is RunStatus.POST_PLAN_COMPLETED:
            run_queue_job.run.handle_post_plan_completed()

        # Handle confirmed, starting pre-apply tasks
        elif run_queue_job.run.status is RunStatus.CONFIRMED:
            run_queue_job.run.handle_confirmed()

        # Check status of pre-apply tasks
        elif run_queue_job.run.status is RunStatus.PRE_APPLY_RUNNING:
            run_queue_job.run.handle_pre_apply_running()
        
        else:
            print(f'Unknown job status for worker: {run_queue_job.run.status}')

    def stop(self):
        """Mark as stopped, stopping any further jobs from executing"""
        self.__running = False

    def wait_for_jobs(self):
        """Wait for any running jobs to complete"""
        self.__job_run_subprocess.join()

    def start(self):
        """Start threads for agent"""
        signal.signal(signal.SIGINT, self.stop)
        #signal.pause()
        self.__job_run_subprocess.start()

    def stop(self, *args):
        """Stop agent"""
        print('Stopping worker... waiting for remaining jobs to complete.')
        self.__running = False
        self.wait_for_jobs()
