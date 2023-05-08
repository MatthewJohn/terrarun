
import signal
import time

import schedule
from terrarun.database import Database

from terrarun.models.authorised_repo import AuthorisedRepo
from terrarun.models.configuration import ConfigurationVersion
from terrarun.models.run import Run


class CronTasks:
    """Interface to start cron tasks."""

    def __init__(self):
        """Store member variables"""
        self._running = True
        schedule.every(60).seconds.do(self.check_for_vcs_commits)

    def stop(self):
        """Mark as stopped, stopping any further jobs from executing"""
        self._running = False

    def start(self):
        """Start scheduler"""
        signal.signal(signal.SIGINT, self.stop)
        #signal.pause()
        while self._running:
            schedule.run_pending()
            time.sleep(1)

    def _process_authorised_repo_workspace(self, authorised_repo, workspace, branch_shas):
        """Handle checking workspace for new commits to create run for"""
        print(f'Handling workspace: {workspace.name}')
        service_provider = authorised_repo.oauth_token.oauth_client.service_provider_instance
        workspace_branch = workspace.get_branch()

        # Obtain latest sha for branch, if not already cached
        if workspace_branch not in branch_shas:
            branch_shas[workspace_branch] =  service_provider.get_latest_commit_ref(
                authorised_repo=workspace.authorised_repo, branch=workspace_branch
            )
        if not branch_shas[workspace_branch]:
            print(f'Could not find latest commit for branch: {workspace_branch}')
            return branch_shas

        if not ConfigurationVersion.get_configuration_version_by_git_commit_sha(
                workspace=workspace,
                git_commit_sha=branch_shas[workspace_branch]):
            # If there is not a configuration version for the git commit,
            # create one
            cv = ConfigurationVersion.generate_from_vcs(
                workspace=workspace,
                commit_ref=branch_shas[workspace_branch],
                # Allow all runs to be queued to be applied
                speculative=False
            )
            if not cv:
                print('Unable to create configuration version')
                return branch_shas

            # Create run
            Run.create(
                configuration_version=cv,
                created_by=None,
                is_destroy=False,
                refresh=True,
                refresh_only=False,
                auto_apply=workspace.auto_apply,
                plan_only=False
            )
        return branch_shas

    def check_for_vcs_commits(self):
        """Check for new commits on VCS repositories"""
        # Iterate over all authorised repos that have one workspace or project defined
        for authorised_repo in AuthorisedRepo.get_all_utilised_repos():
            print(f'Handling repo: {authorised_repo.name}')
            branch_shas = {}

            for project in authorised_repo.projects:
                print(f'Handling project: {project.name}')

                for workspace in project.workspaces:
                    branch_shas = self._process_authorised_repo_workspace(
                        authorised_repo=authorised_repo,
                        workspace=workspace,
                        branch_shas=branch_shas
                    )

            # Handle direct member workspaces
            for workspace in authorised_repo.workspaces:
                branch_shas = self._process_authorised_repo_workspace(
                    authorised_repo=authorised_repo,
                    workspace=workspace,
                    branch_shas=branch_shas
                )

        # Clear database session to avoid cached queries
        Database.get_session().remove()

        print("Checking for VCS commits")
