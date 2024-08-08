# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0

class OrganisationPermissionSet:

    def __init__(self):
        """Initialise all permissions to false."""
        self._can_access_via_teams = False
        self._can_create_module = False
        self._can_create_provider = False
        self._can_create_team = False
        self._can_create_workspace = False
        self._can_destroy = False
        self._can_manage_custom_providers = False
        self._can_manage_public_modules = False
        self._can_manage_public_providers = False
        self._can_manage_run_tasks = False
        self._can_manage_sso = False
        self._can_manage_subscriptions = False
        self._can_manage_tags = False
        self._can_manage_users = False
        self._can_manage_varsets = False
        self._can_read_run_tasks = False
        self._can_read_varsets = False
        self._can_start_trial = False
        self._can_traverse = False
        self._can_update_agent_pools = False
        self._can_update_api_token = False
        self._can_update = False
        self._can_update_oauth = False
        self._can_update_sentinel = False
        self._can_update_ssh_keys = False


    @property
    def can_update(self):
        """Return permission can_update"""
        return self._can_update

    @property
    def can_destroy(self):
        """Return permission can_destroy"""
        return self._can_destroy

    @property
    def can_access_via_teams(self):
        """Return permission can_access_via_teams"""
        return self._can_access_via_teams

    @property
    def can_create_module(self):
        """Return permission can_create_module"""
        return self._can_create_module

    @property
    def can_create_team(self):
        """Return permission can_create_team"""
        return self._can_create_team

    @property
    def can_create_workspace(self):
        """Return permission can_create_workspace"""
        return self._can_create_workspace

    @property
    def can_manage_users(self):
        """Return permission can_manage_users"""
        return self._can_manage_users

    @property
    def can_manage_subscriptions(self):
        """Return permission can_manage_subscriptions"""
        return self._can_manage_subscriptions

    @property
    def can_manage_sso(self):
        """Return permission can_manage_sso"""
        return self._can_manage_sso

    @property
    def can_update_oauth(self):
        """Return permission can_update_oauth"""
        return self._can_update_oauth

    @property
    def can_update_sentinel(self):
        """Return permission can_update_sentinel"""
        return self._can_update_sentinel

    @property
    def can_update_ssh_keys(self):
        """Return permission can_update_ssh_keys"""
        return self._can_update_ssh_keys

    @property
    def can_update_api_token(self):
        """Return permission can_update_api_token"""
        return self._can_update_api_token

    @property
    def can_traverse(self):
        """Return permission can_traverse"""
        return self._can_traverse

    @property
    def can_start_trial(self):
        """Return permission can_start_trial"""
        return self._can_start_trial

    @property
    def can_update_agent_pools(self):
        """Return permission can_update_agent_pools"""
        return self._can_update_agent_pools

    @property
    def can_manage_tags(self):
        """Return permission can_manage_tags"""
        return self._can_manage_tags

    @property
    def can_manage_varsets(self):
        """Return permission can_manage_varsets"""
        return self._can_manage_varsets

    @property
    def can_read_varsets(self):
        """Return permission can_read_varsets"""
        return self._can_read_varsets

    @property
    def can_manage_public_providers(self):
        """Return permission can_manage_public_providers"""
        return self._can_manage_public_providers

    @property
    def can_create_provider(self):
        """Return permission can_create_provider"""
        return self._can_create_provider

    @property
    def can_manage_public_modules(self):
        """Return permission can_manage_public_modules"""
        return self._can_manage_public_modules

    @property
    def can_manage_custom_providers(self):
        """Return permission can_manage_custom_providers"""
        return self._can_manage_custom_providers

    @property
    def can_manage_run_tasks(self):
        """Return permission can_manage_run_tasks"""
        return self._can_manage_run_tasks

    @property
    def can_read_run_tasks(self):
        """Return permission can_read_run_tasks"""
        return self._can_read_run_tasks


    def get_api_details(self):
        return {
            "can-update": self.can_update,
            "can-destroy": self.can_destroy,
            "can-access-via-teams": self.can_access_via_teams,
            "can-create-module": self.can_create_module,
            "can-create-team": self.can_create_team,
            "can-create-workspace": self.can_create_workspace,
            "can-manage-users": self.can_manage_users,
            "can-manage-subscription": self.can_manage_subscriptions,
            "can-manage-sso": self.can_manage_sso,
            "can-update-oauth": self.can_update_oauth,
            "can-update-sentinel": self.can_update_sentinel,
            "can-update-ssh-keys": self.can_update_ssh_keys,
            "can-update-api-token": self.can_update_api_token,
            "can-traverse": self.can_traverse,
            "can-start-trial": self.can_start_trial,
            "can-update-agent-pools": self.can_update_agent_pools,
            "can-manage-tags": self.can_manage_tags,
            "can-manage-varsets": self.can_manage_varsets,
            "can-read-varsets": self.can_read_varsets,
            "can-manage-public-providers": self.can_manage_public_providers,
            "can-create-provider": self.can_create_provider,
            "can-manage-public-modules": self.can_manage_public_modules,
            "can-manage-custom-providers": self.can_manage_custom_providers,
            "can-manage-run-tasks": self.can_manage_run_tasks,
            "can-read-run-tasks": self.can_read_run_tasks
        }
