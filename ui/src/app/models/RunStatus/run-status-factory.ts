import { Injectable } from "@angular/core";
import { IRunStatus } from "./run-status";
import { RunStatusEnum } from "./run-status-enum";

abstract class RunStatusBaseClass implements IRunStatus {
    public abstract _nameString: string;
    public abstract _labelColour: string;
    public abstract _icon: string;

    getName(): string {
        return this._nameString
    };
    getColor(): string {
        return this._labelColour
    }
    getIcon(): string {
        return this._icon;
    }
}

class RunStatusApplied extends RunStatusBaseClass {
    _nameString = "Applied";
    _labelColour = "green";
    _icon = "done-all-outline";
}
class RunStatusApplying extends RunStatusBaseClass {
    _nameString = "Applying";
    _labelColour = "green";
    _icon = "activity-outline";
}
class RunStatusApplyQueued extends RunStatusBaseClass {
    _nameString = "Applying";
    _labelColour = "green";
    _icon = "radio-button-on-outline";
}
class RunStatusCancelled extends RunStatusBaseClass {
    _nameString = "Cancelled";
    _labelColour = "green";
    _icon = "alert-circle-outline";
}
class RunStatusConfirmed extends RunStatusBaseClass {
    _nameString = "Confirmed";
    _labelColour = "green";
    _icon = "radio-button-on-outline";
}
class RunStatusCostEstimated extends RunStatusBaseClass {
    _nameString = "Cost estimated";
    _labelColour = "green";
    _icon = "radio-button-on-outline";
}
class RunStatusCostEstimating extends RunStatusBaseClass {
    _nameString = "Cost estimating";
    _labelColour = "green";
    _icon = "radio-button-on-outline";
}
class RunStatusDiscarded extends RunStatusBaseClass {
    _nameString = "Discarded";
    _labelColour = "green";
    _icon = "alert-circle-outline";
}
class RunStatusErrored extends RunStatusBaseClass {
    _nameString = "Errored";
    _labelColour = "green";
    _icon = "alert-circle-outline";
}
class RunStatusFetching extends RunStatusBaseClass {
    _nameString = "Fetching";
    _labelColour = "green";
    _icon = "radio-button-on-outline";
}
class RunStatusForceCancelled extends RunStatusBaseClass {
    _nameString = "Force cancelled";
    _labelColour = "green";
    _icon = "radio-button-on-outline";
}
class RunStatusPending extends RunStatusBaseClass {
    _nameString = "Pending";
    _labelColour = "green";
    _icon = "radio-button-on-outline";
}
class RunStatusPlanned extends RunStatusBaseClass {
    _nameString = "Planned";
    _labelColour = "green";
    _icon = "checkmark-square-outline";
}
class RunStatusPlannedAndFinished extends RunStatusBaseClass {
    _nameString = "Planned and finished";
    _labelColour = "green";
    _icon = "checkmark-outline";
}
class RunStatusPlanning extends RunStatusBaseClass {
    _nameString = "Planning";
    _labelColour = "green";
    _icon = "activity-outline";
}
class RunStatusPlanQueued extends RunStatusBaseClass {
    _nameString = "Plan queued";
    _labelColour = "green";
    _icon = "radio-button-on-outline";
}
class RunStatusPolicyChecked extends RunStatusBaseClass {
    _nameString = "Policy checked";
    _labelColour = "green";
    _icon = "radio-button-on-outline";
}
class RunStatusPolicyChecking extends RunStatusBaseClass {
    _nameString = "Policy checking";
    _labelColour = "green";
    _icon = "radio-button-on-outline";
}
class RunStatusPolicyOverride extends RunStatusBaseClass {
    _nameString = "Policy override";
    _labelColour = "green";
    _icon = "alert-triangle-outline";
}
class RunStatusPolicySoftFailed extends RunStatusBaseClass {
    _nameString = "Policy soft failed";
    _labelColour = "green";
    _icon = "alert-triangle-outline";
}
class RunStatusPostPlanCompleted extends RunStatusBaseClass {
    _nameString = "Post-plan completed";
    _labelColour = "green";
    _icon = "radio-button-on-outline";
}
class RunStatusPostPlanRunning extends RunStatusBaseClass {
    _nameString = "Post-plan running";
    _labelColour = "green";
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

