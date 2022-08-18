import { Injectable } from "@angular/core";
import { RunAction } from "../RunAction/run-action-enum";
import { IRunStatus } from "./run-status";
import { RunStatusEnum } from "./run-status-enum";

abstract class RunStatusBaseClass implements IRunStatus {
    public abstract _nameString: string;
    public abstract _labelColour: string;
    public abstract _icon: string;
    public _availableActions: RunAction[] = [];

    getName(): string {
        return this._nameString
    };
    getColor(): string {
        return this._labelColour
    }
    getIcon(): string {
        return this._icon;
    }
    getAvailableActions(): RunAction[] {
        return this._availableActions;
    }
}

class RunStatusApplied extends RunStatusBaseClass {
    _nameString = "Applied";
    _labelColour = "success";
    _icon = "done-all-outline";
}
class RunStatusApplying extends RunStatusBaseClass {
    _nameString = "Applying";
    _labelColour = "info";
    _icon = "activity-outline";
    public override _availableActions = [RunAction.CANCEL_RUN];
}
class RunStatusApplyQueued extends RunStatusBaseClass {
    _nameString = "Applying";
    _labelColour = "info";
    _icon = "radio-button-on-outline";
}
class RunStatusCancelled extends RunStatusBaseClass {
    _nameString = "Cancelled";
    _labelColour = "danger";
    _icon = "alert-circle-outline";
    public override _availableActions = [RunAction.FORCE_CANCEL_RUN];
}
class RunStatusConfirmed extends RunStatusBaseClass {
    _nameString = "Confirmed";
    _labelColour = "basic";
    _icon = "radio-button-on-outline";
}
class RunStatusCostEstimated extends RunStatusBaseClass {
    _nameString = "Cost estimated";
    _labelColour = "info";
    _icon = "radio-button-on-outline";
}
class RunStatusCostEstimating extends RunStatusBaseClass {
    _nameString = "Cost estimating";
    _labelColour = "info";
    _icon = "radio-button-on-outline";
}
class RunStatusDiscarded extends RunStatusBaseClass {
    _nameString = "Discarded";
    _labelColour = "danger";
    _icon = "alert-circle-outline";
}
class RunStatusErrored extends RunStatusBaseClass {
    _nameString = "Errored";
    _labelColour = "danger";
    _icon = "alert-circle-outline";
}
class RunStatusFetching extends RunStatusBaseClass {
    _nameString = "Fetching";
    _labelColour = "info";
    _icon = "radio-button-on-outline";
}
class RunStatusForceCancelled extends RunStatusBaseClass {
    _nameString = "Force cancelled";
    _labelColour = "warning";
    _icon = "radio-button-on-outline";
}
class RunStatusPending extends RunStatusBaseClass {
    _nameString = "Pending";
    _labelColour = "basic";
    _icon = "radio-button-on-outline";
}
class RunStatusPlanned extends RunStatusBaseClass {
    _nameString = "Planned";
    _labelColour = "success";
    _icon = "checkmark-square-outline";
    public override _availableActions = [RunAction.CONFIRM_AND_APPLY];
}
class RunStatusPlannedAndFinished extends RunStatusBaseClass {
    _nameString = "Planned and finished";
    _labelColour = "success";
    _icon = "checkmark-outline";
}
class RunStatusPlanning extends RunStatusBaseClass {
    _nameString = "Planning";
    _labelColour = "info";
    _icon = "activity-outline";
    public override _availableActions = [RunAction.CANCEL_RUN];
}
class RunStatusPlanQueued extends RunStatusBaseClass {
    _nameString = "Plan queued";
    _labelColour = "info";
    _icon = "radio-button-on-outline";
}
class RunStatusPolicyChecked extends RunStatusBaseClass {
    _nameString = "Policy checked";
    _labelColour = "info";
    _icon = "radio-button-on-outline";
}
class RunStatusPolicyChecking extends RunStatusBaseClass {
    _nameString = "Policy checking";
    _labelColour = "info";
    _icon = "radio-button-on-outline";
}
class RunStatusPolicyOverride extends RunStatusBaseClass {
    _nameString = "Policy override";
    _labelColour = "warning";
    _icon = "alert-triangle-outline";
}
class RunStatusPolicySoftFailed extends RunStatusBaseClass {
    _nameString = "Policy soft failed";
    _labelColour = "warning";
    _icon = "alert-triangle-outline";
    public override _availableActions = [RunAction.OVERRIDE_AND_CONTINUE];
}
class RunStatusPostPlanCompleted extends RunStatusBaseClass {
    _nameString = "Post-plan completed";
    _labelColour = "success";
    _icon = "radio-button-on-outline";
}
class RunStatusPostPlanRunning extends RunStatusBaseClass {
    _nameString = "Post-plan running";
    _labelColour = "info";
    _icon = "radio-button-on-outline";
}


const RunStatusMap: Record<RunStatusEnum, new (...args: any[]) => IRunStatus> = {
    [RunStatusEnum.APPLIED]: RunStatusApplied,
    [RunStatusEnum.APPLYING]: RunStatusApplying,
    [RunStatusEnum.APPLY_QUEUED]: RunStatusApplyQueued,
    [RunStatusEnum.CANCELED]: RunStatusCancelled,
    [RunStatusEnum.CONFIRMED]: RunStatusConfirmed,
    [RunStatusEnum.COST_ESTIMATED]: RunStatusCostEstimated,
    [RunStatusEnum.COST_ESTIMATING]: RunStatusCostEstimating,
    [RunStatusEnum.DISCARDED]: RunStatusDiscarded,
    [RunStatusEnum.ERRORED]: RunStatusErrored,
    [RunStatusEnum.FETCHING]: RunStatusFetching,
    [RunStatusEnum.FORCE_CANCELLED]: RunStatusForceCancelled,
    [RunStatusEnum.PENDING]: RunStatusPending,
    [RunStatusEnum.PLANNED]: RunStatusPlanned,
    [RunStatusEnum.PLANNED_AND_FINISHED]: RunStatusPlannedAndFinished,
    [RunStatusEnum.PLANNING]: RunStatusPlanning,
    [RunStatusEnum.PLAN_QUEUED]: RunStatusPlanQueued,
    [RunStatusEnum.POLICY_CHECKED]: RunStatusPolicyChecked,
    [RunStatusEnum.POLICY_CHECKING]: RunStatusPolicyChecking,
    [RunStatusEnum.POLICY_OVERRIDE]: RunStatusPolicyOverride,
    [RunStatusEnum.POLICY_SOFT_FAILED]: RunStatusPolicySoftFailed,
    [RunStatusEnum.POST_PLAN_COMPLETED]: RunStatusPostPlanCompleted,
    [RunStatusEnum.POST_PLAN_RUNNING]: RunStatusPostPlanRunning,
}

@Injectable({
    providedIn: 'root'
  })
export class RunStatusFactory {

    // @TODO Update signure to match instance of 'new (...args: any[]) => IRunStatus)'
    getStatusByValue(statusEnumValue: string): any {
        return new RunStatusMap[statusEnumValue as RunStatusEnum]();
    }
}

