# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0


import re
import signal
import time
import fnmatch

import schedule
from terrarun.database import Database
from terrarun.logger import get_logger

from terrarun.models.authorised_repo import AuthorisedRepo
from terrarun.models.configuration import ConfigurationVersion
from terrarun.models.run import Run


log = get_logger(__name__)


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
        log.debug(f'Handling workspace: {workspace.name}')
        service_provider = authorised_repo.oauth_token.oauth_client.service_provider_instance

        commit_sha = None
        workspace_branch = None
        workspace_tag = None

        # Handle workspaces with git tag regex
        if workspace.vcs_repo_tags_regex:
            log.debug("Handling tag-based search")
            tag_re = re.compile(workspace.vcs_repo_tags_regex)
            tags = service_provider.get_tags(
                authorised_repo=workspace.authorised_repo
            )
            for tag in tags:
                log.debug(f"Checking tag: {tag}")
                if tag_re.match(tag):
                    log.debug("Tag matches regex")
                    # Once a match tag is found, check if there is a run for it
                    if not ConfigurationVersion.get_configuration_version_by_git_commit_sha(
                            workspace=workspace,
                            git_commit_sha=tags[tag]):
                        # If there wasn't, perform a run with the commit sha
                        commit_sha = tags[tag]
                        workspace_tag = tag
                        log.debug(f"Using tag commit {tags[tag]}")
                    else:
                        log.debug(f"Run already exists for commit {tags[tag]}")

                    # Otherwise, the commit sha is not set, but exit
                    # as all other tags are older
                    break
                else:
                    log.debug("Tag does not match regex")

        else:
            workspace_branch = workspace.get_branch()

            # Obtain latest sha for branch, if not already cached
            if workspace_branch not in branch_shas:
                branch_shas[workspace_branch] =  service_provider.get_latest_commit_ref(
                    authorised_repo=workspace.authorised_repo, branch=workspace_branch
                )

            if not branch_shas[workspace_branch]:
                log.warning(f'Could not find latest commit for branch: {workspace_branch}')
                return branch_shas

            if not ConfigurationVersion.get_configuration_version_by_git_commit_sha(
                    workspace=workspace,
                    git_commit_sha=branch_shas[workspace_branch]):
                commit_sha = branch_shas[workspace_branch]

                # Check if filters match
                if workspace.trigger_patterns or workspace.trigger_prefixes:
                    log.debug("Trigger pattern/prefixes enabled")
                    latest_configuration_version = workspace.latest_configuration_version
                    # If there is a configuration version and it contains a git sha...
                    if latest_configuration_version and latest_configuration_version.git_commit_sha:
                        # Get the file changes between the commits
                        file_changes = service_provider.get_changed_files(
                            authorised_repo=workspace.authorised_repo,
                            base=latest_configuration_version.git_commit_sha,
                            head=commit_sha
                        )
                        log.debug(f"Found file changes: {file_changes}")
                        if workspace.trigger_patterns:
                            log.debug("Checking trigger patterns")
                            for trigger_pattern in workspace.trigger_patterns:
                                log.debug(f"Checking pattern: {trigger_pattern}")
                                # If any of the filters match, break
                                if fnmatch.filter(file_changes, trigger_pattern):
                                    log.debug("Pattern matched")
                                    break
                            else:
                                # If no match was found, unset commit sha to avoid build
                                log.debug('No patterns matched')
                                commit_sha = None

                        elif workspace.trigger_prefixes:
                            log.debug("Checking trigger prefixes")

                            for trigger_prefix in workspace.trigger_prefixes:
                                log.debug(f"Checking prefix: {trigger_prefix}")

                                if filter(lambda x: x.startswith(trigger_prefix), file_changes):
                                    log.debug("Prefix matched")
                                    break
                            else:
                                log.debug('No prefixes matched')
                                commit_sha = None

                    else:
                        log.warning("No latest configuration version found or "
                                    "latest configuration version has no commit ID")

        if commit_sha is not None:
            log.info(f"Creating configuration version for commit {commit_sha}")
            # If there is not a configuration version for the git commit,
            # create one
            cv = ConfigurationVersion.generate_from_vcs(
                workspace=workspace,
                commit_ref=commit_sha,
                # Allow all runs to be queued to be applied
                speculative=False,
                branch=workspace_branch,
                tag=workspace_tag
            )
            if not cv:
                log.info('Unable to create configuration version')
                return branch_shas

            # Create run
            if workspace.queue_all_runs:
                log.info(f"Creating run")
                try:
                    Run.create(
                        configuration_version=cv,
                        created_by=None,
                        is_destroy=False,
                        refresh=True,
                        refresh_only=False,
                        auto_apply=workspace.auto_apply,
                        plan_only=False,
                        message="Initiated from SCM change"
                    )
                # @TODO Limit to legitimate errors, such as environment progression
                # errors
                except Exception as exc:
                    log.error(f"failed to start run: {exc}")
            else:
                log.info("Skipping run creation as workspace not configured with queue_all_runs")
        return branch_shas

    def check_for_vcs_commits(self):
        """Check for new commits on VCS repositories"""
        log.info("Checking for VCS commits")

        # Iterate over all authorised repos that have one workspace or project defined
        for authorised_repo in AuthorisedRepo.get_all_utilised_repos():
            log.debug(f'Handling repo: {authorised_repo.name}')
            branch_shas = {}

            for project in authorised_repo.projects:
                log.debug(f'Handling project: {project.name}')

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
