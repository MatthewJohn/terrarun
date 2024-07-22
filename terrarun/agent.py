# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0


import datetime
import signal
import threading
from time import sleep

import requests

from terrarun.models.agent import AgentStatus


class AgentConfig:

    def __init__(self, address, token):
        """Store member variables"""
        self.__address = address
        self.__token = token

    @property
    def address(self):
        """Return address"""
        return self.__address

    @property
    def token(self):
        """Return token"""
        return self.__token


class AgentRuntimeConfig:

    @classmethod
    def create_from_registration_response(cls, registration_response):
        """Create runtime config from registration response"""
        if not (id := registration_response.get("id")):
            raise Exception('Agent id not provided in registration response')
        
        return cls(
            id=id
        )

    def __init__(self, id):
        """Store details about agent"""
        self.__id = id

    @property
    def id(self):
        """Return agent id"""
        return self.__id


class AgentJob:
    """Store information about current agent job"""

    def __init__(self, job_id):
        """Store member variables"""
        self._job_id = job_id
        self._start_time = datetime.datetime.now()


class Agent:
    """Provide functionality for agent"""

    REQUEST_TIMEOUT = 30

    def __init__(self, agent_config):
        """Store member variables"""
        self.__agent_config: AgentConfig = agent_config
        self.__current_job: AgentJob = None
        self.__runtime_config: AgentRuntimeConfig = None
        self.__running = True

    def register_agent(self):
        """Register agent with Terrarun"""
        res = requests.post(
            f"{self.__agent_config.address}/api/agent/register",
            timeout=self.REQUEST_TIMEOUT,
            headers={
                'Authorization': f'Bearer {self.__agent_config.token}'
            }
        )
        if res.status_code == 403:
            raise Exception('Invalid agent token provided')
        elif res.status_code != 200:
            raise Exception(f'Invalid response from registration endpoint: {res.status_code}')

        self.__runtime_config = AgentRuntimeConfig.create_from_registration_response(res.json())
        print(f'Agent registered with ID: {self.__runtime_config.id}')

    def check_for_jobs_loop(self):
        """Enter loop to continue looking for jobs"""
        while self.__running:
            self._check_for_jobs()
            sleep(5)

    def _check_for_jobs(self):
        """Check for jobs to run"""
        print('Checking for jobs...')

    def _push_agent_status(self):
        """Push agent status"""
        status = (
            AgentStatus.EXITED if not self.__running  else (
                AgentStatus.BUSY if self.__current_job else AgentStatus.IDLE
            )
        )
        print(f"Pushing agent status: {status.value}")
        res = requests.put(
            f"{self.__agent_config.address}/api/agent/status",
            json={
                "status": status.value
            },
            timeout=self.REQUEST_TIMEOUT,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.__agent_config.token}",
                "Tfc-Agent-Id": self.__runtime_config.id
            }
        )
        if res.status_code != 200:
            print(f'Error: Failed to push metrics: {res.status_code}')

    def push_agent_status_loop(self):
        """Push agent status"""
        while self.__running:
            self._push_agent_status()
            sleep(30)

    def stop(self):
        """Mark as stopped, stopping any further jobs from executing"""
        self.__running = False

    def wait_for_jobs(self):
        """Wait for any running jobs to complete"""
        pass

    def set_exited_status(self):
        """Set exited status"""
        self._push_agent_status()


class AgentProcessHandler:

    def __init__(self, agent: Agent):
        """Store member variables"""
        self.__agent = agent
        self.__status_subprocess = threading.Thread(target=self.__agent.push_agent_status_loop)
        self.__job_run_subprocess = threading.Thread(target=self.__agent.check_for_jobs_loop)

    def start(self):
        """Start threads for agent"""
        signal.signal(signal.SIGINT, self.stop)
        #signal.pause()
        self.__agent.register_agent()
        self.__status_subprocess.start()
        self.__job_run_subprocess.start()

    def stop(self, *args):
        """Stop agent"""
        print('Stopping agent... waiting for remaining jobs to complete.')
        self.__agent.stop()
        self.__agent.wait_for_jobs()
        self.__agent.set_exited_status()
