# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0

from enum import Enum
from typing import Optional, Dict

import terrarun.models.run


class RunStatus(Enum):

    PENDING = 'pending'
    FETCHING = 'fetching'
    FETCHING_COMPLETED = 'fetching_completed'
    PRE_PLAN_RUNNING = 'pre_plan_running'
    PRE_PLAN_COMPLETED = 'pre_plan_completed'
    QUEUING = 'queuing'
    PLAN_QUEUED = 'plan_queued'
    PLANNING = 'planning'
    PLANNED = 'planned'
    COST_ESTIMATING = 'cost_estimating'
    COST_ESTIMATED = 'cost_estimated'
    POLICY_CHECKING = 'policy_checking'
    POLICY_OVERRIDE = 'policy_override'
    POLICY_SOFT_FAILED = 'policy_soft_failed'
    POLICY_CHECKED = 'policy_checked'
    CONFIRMED = 'confirmed'
    POST_PLAN_RUNNING = 'post_plan_running'
    POST_PLAN_COMPLETED = 'post_plan_completed'
    PLANNED_AND_FINISHED = 'planned_and_finished'
    PRE_APPLY_RUNNING = 'pre_apply_running'  # Not yet part of official documentation
    PRE_APPLY_COMPLETED = 'pre_apply_completed'  # Not yet part of official documentation
    APPLY_QUEUED = 'apply_queued'
    APPLYING = 'applying'
    APPLIED = 'applied'
    DISCARDED = 'discarded'
    ERRORED = 'errored'
    CANCELED = 'canceled'
    FORCE_CANCELLED = 'force_canceled'


class BaseRunFlow:

    ENUM: Optional['RunStatus'] = None
    IS_CANCELABLE: bool = False
    IS_CONFIRMABLE: bool = False
    IS_DISCARDABLE: bool = False
    IS_FORCE_CANCELABLE: bool = False

    def get_run_actions(self) -> Dict[str, bool]:
        """Return Run actions for API response"""
        return {
            "is-cancelable": self.IS_CANCELABLE,
            "is-confirmable": self.IS_CONFIRMABLE,
            "is-discardable": self.IS_DISCARDABLE,
            "is-force-cancelable": self.IS_FORCE_CANCELABLE
        }


class RunFlowPending(BaseRunFlow):

    ENUM = RunStatus.PENDING
    IS_CANCELABLE = True


class RunFlowFetching(BaseRunFlow):

    ENUM = RunStatus.FETCHING
    IS_CANCELABLE = True


class RunFlowFetchingCompleted(BaseRunFlow):

    ENUM = RunStatus.FETCHING_COMPLETED
    IS_CANCELABLE = True


class RunFlowPrePlanRunning(BaseRunFlow):

    ENUM = RunStatus.PRE_PLAN_RUNNING
    IS_CANCELABLE = True


class RunFlowPrePlanCompleted(BaseRunFlow):

    ENUM = RunStatus.PRE_PLAN_COMPLETED
    IS_CANCELABLE = True


class RunFlowQueuing(BaseRunFlow):

    ENUM = RunStatus.QUEUING
    IS_CANCELABLE = True


class RunFlowPlanQueued(BaseRunFlow):

    ENUM = RunStatus.PLAN_QUEUED


class RunFlowPlanning(BaseRunFlow):

    ENUM = RunStatus.PLANNING


class RunFlowPlanned(BaseRunFlow):

    ENUM = RunStatus.PLANNED
    IS_CONFIRMABLE = True


class RunFlowCostEstimating(BaseRunFlow):

    ENUM = RunStatus.COST_ESTIMATING
    IS_CONFIRMABLE = True


class RunFlowCostEstimated(BaseRunFlow):

    ENUM = RunStatus.COST_ESTIMATED
    IS_CONFIRMABLE = True


class RunFlowPolicyChecking(BaseRunFlow):

    ENUM = RunStatus.POLICY_CHECKING


class RunFlowPolicyOverride(BaseRunFlow):

    ENUM = RunStatus.POLICY_OVERRIDE


class RunFlowPolicySoftFailed(BaseRunFlow):

    ENUM = RunStatus.POLICY_SOFT_FAILED


class RunFlowPolicyChecked(BaseRunFlow):

    ENUM = RunStatus.POLICY_CHECKED


class RunFlowConfirmed(BaseRunFlow):

    ENUM = RunStatus.CONFIRMED
    IS_CANCELABLE = True


class RunFlowPostPlanRunning(BaseRunFlow):

    ENUM = RunStatus.POST_PLAN_RUNNING
    IS_CONFIRMABLE = True


class RunFlowPostPlanCompleted(BaseRunFlow):

    ENUM = RunStatus.POST_PLAN_COMPLETED
    IS_CONFIRMABLE = True


class RunFlowPlannedAndFinished(BaseRunFlow):

    ENUM = RunStatus.PLANNED_AND_FINISHED


class RunFlowPreApplyRunning(BaseRunFlow):

    ENUM = RunStatus.PRE_APPLY_RUNNING


class RunFlowPreApplyCompleted(BaseRunFlow):

    ENUM = RunStatus.PRE_APPLY_COMPLETED


class RunFlowApplyQueued(BaseRunFlow):

    ENUM = RunStatus.APPLY_QUEUED
    IS_CANCELABLE = True


class RunFlowApplying(BaseRunFlow):

    ENUM = RunStatus.APPLYING


class RunFlowApplied(BaseRunFlow):

    ENUM = RunStatus.APPLIED


class RunFlowDiscarded(BaseRunFlow):

    ENUM = RunStatus.DISCARDED


class RunFlowErrored(BaseRunFlow):

    ENUM = RunStatus.ERRORED


class RunFlowCanceled(BaseRunFlow):

    ENUM = RunStatus.CANCELED


class RunFlowForceCancelled(BaseRunFlow):

    ENUM = RunStatus.FORCE_CANCELLED



class RunFlowFactory:

    _FLOW_LOOKUP: Optional[Dict['RunStatus', type['BaseRunFlow']]] = None

    @classmethod
    def get_flow_lookup(cls) -> Dict['RunStatus', type['BaseRunFlow']]:
        """Obtain flow lookup dict"""
        if cls._FLOW_LOOKUP is None:
            cls._FLOW_LOOKUP = {
                cls_.ENUM: cls_
                for cls_ in BaseRunFlow.__subclasses__()
                if cls_.ENUM is not None
            }
        return cls._FLOW_LOOKUP

    @classmethod
    def get_flow_by_status(cls, status: 'RunStatus') -> Optional['BaseRunFlow']:
        """Return flow based on status"""
        flow_cls = cls.get_flow_lookup().get(status)
        if flow_cls:
            return flow_cls()
