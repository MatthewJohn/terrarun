import { Injectable } from "@angular/core";
import { RunAction } from "../RunAction/run-action-enum";
import { IRunStatus } from "./run-status";
import { RunStatusEnum } from "./run-status-enum";

abstract class RunStatusBaseClass implements IRunStatus {
    public abstract _nameString: string;
    public abstract _labelColour: string;
    public abstract _icon: string;
    public _availableActions: RunAction[] = [];
    public _shouldCheckPrePlan: boolean = false;
    public _shouldCheckPlan: boolean = false;
    public _shouldCheckPostPlan: boolean = false;
    public _shouldCheckPreApply: boolean = false;
    public _shouldCheckApply: boolean = false;
    public _isFinal: boolean = false;

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
    isFinal(): boolean {
        return this._isFinal;
    }
    shouldCheckPrePlan(): boolean {
        return this._shouldCheckPrePlan;
    }
    shouldCheckPlan(): boolean {
        return this._shouldCheckPlan;
    }
    shouldCheckPostPlan(): boolean {
        return this._shouldCheckPostPlan;
    }
    shouldCheckPreApply(): boolean {
        return this._shouldCheckPreApply;
    }
    shouldCheckApply(): boolean {
        return this._shouldCheckApply;
    }
}

class RunStatusApplied extends RunStatusBaseClass {
    _nameString = "Applied";
    _labelColour = "success";
    _icon = "done-all-outline";
    public override _isFinal = true;
    public override _availableActions = [RunAction.RETRY_RUN];
}
class RunStatusApplying extends RunStatusBaseClass {
    _nameString = "Applying";
    _labelColour = "basic";
    _icon = "activity-outline";
    public override _availableActions = [RunAction.CANCEL_RUN];
    public override _shouldCheckApply = true;
}
class RunStatusApplyQueued extends RunStatusBaseClass {
    _nameString = "Apply queued";
    _labelColour = "basic";
    _icon = "radio-button-on-outline";
}
class RunStatusCancelled extends RunStatusBaseClass {
    _nameString = "Cancelled";
    _labelColour = "danger";
    _icon = "alert-circle-outline";
    public override _availableActions = [RunAction.FORCE_CANCEL_RUN];
    public override _isFinal = true;
}
class RunStatusConfirmed extends RunStatusBaseClass {
    _nameString = "Confirmed";
    _labelColour = "basic";
    _icon = "radio-button-on-outline";
}
class RunStatusCostEstimated extends RunStatusBaseClass {
    _nameString = "Cost estimated";
    _labelColour = "basic";
    _icon = "radio-button-on-outline";
}
class RunStatusCostEstimating extends RunStatusBaseClass {
    _nameString = "Cost estimating";
    _labelColour = "basic";
    _icon = "radio-button-on-outline";
}
class RunStatusDiscarded extends RunStatusBaseClass {
    _nameString = "Discarded";
    _labelColour = "info";
    _icon = "alert-circle-outline";
    public override _isFinal = true;
    public override _availableActions = [RunAction.RETRY_RUN];
}
class RunStatusErrored extends RunStatusBaseClass {
    _nameString = "Errored";
    _labelColour = "danger";
    _icon = "alert-circle-outline";
    public override _isFinal = true;
    public override _availableActions = [RunAction.RETRY_RUN];
}
class RunStatusFetching extends RunStatusBaseClass {
    _nameString = "Fetching";
    _labelColour = "basic";
    _icon = "radio-button-on-outline";
}
class RunStatusForceCancelled extends RunStatusBaseClass {
    _nameString = "Force cancelled";
    _labelColour = "warning";
    _icon = "radio-button-on-outline";
    public override _availableActions = [RunAction.RETRY_RUN];
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
}
class RunStatusPlannedAndFinished extends RunStatusBaseClass {
    _nameString = "Planned and finished";
    _labelColour = "success";
    _icon = "checkmark-outline";
    public override _isFinal = true;
    public override _availableActions = [RunAction.RETRY_RUN];
}
class RunStatusPlanning extends RunStatusBaseClass {
    _nameString = "Planning";
    _labelColour = "basic";
    _icon = "activity-outline";
    public override _availableActions = [RunAction.CANCEL_RUN];
    public override _shouldCheckPlan = true;
}
class RunStatusPlanQueued extends RunStatusBaseClass {
    _nameString = "Plan queued";
    _labelColour = "basic";
    _icon = "radio-button-on-outline";
}
class RunStatusPolicyChecked extends RunStatusBaseClass {
    _nameString = "Policy checked";
    _labelColour = "basic";
    _icon = "radio-button-on-outline";
}
class RunStatusPolicyChecking extends RunStatusBaseClass {
    _nameString = "Policy checking";
    _labelColour = "basic";
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
    _labelColour = "warning";
    _icon = "radio-button-on-outline";
    public override _availableActions = [RunAction.CONFIRM_AND_APPLY, RunAction.DISCARD_RUN];
}
class RunStatusPostPlanRunning extends RunStatusBaseClass {
    _nameString = "Post-plan running";
    _labelColour = "basic";
    _icon = "radio-button-on-outline";
    public override _shouldCheckPostPlan = true;
}
class RunStatusPrePlanCompleted extends RunStatusBaseClass {
    _nameString = "Pre-plan completed";
    _labelColour = "success";
    _icon = "radio-button-on-outline";
}
class RunStatusPrePlanRunning extends RunStatusBaseClass {
    _nameString = "Pre-plan running";
    _labelColour = "basic";
    _icon = "radio-button-on-outline";
    public override _shouldCheckPrePlan = true;
}
class RunStatusPreApplyCompleted extends RunStatusBaseClass {
    _nameString = "Pre-apply completed";
    _labelColour = "success";
    _icon = "radio-button-on-outline";
}
class RunStatusPreApplyRunning extends RunStatusBaseClass {
    _nameString = "Pre-apply running";
    _labelColour = "basic";
    _icon = "radio-button-on-outline";
    public override _shouldCheckPreApply = true;
}
class RunStatusQueuing extends RunStatusBaseClass {
    _nameString = "Queuing";
    _labelColour = "basic";
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
    [RunStatusEnum.PRE_PLAN_COMPLETED]: RunStatusPrePlanCompleted,
    [RunStatusEnum.PRE_PLAN_RUNNING]: RunStatusPrePlanRunning,
    [RunStatusEnum.PRE_APPLY_COMPLETED]: RunStatusPreApplyCompleted,
    [RunStatusEnum.PRE_APPLY_RUNNING]: RunStatusPreApplyRunning,
    [RunStatusEnum.QUEUING]: RunStatusQueuing
}

@Injectable({
    providedIn: 'root'
})
export class RunStatusFactory {

    // @TODO Update signure to match instance of 'new (...args: any[]) => IRunStatus)'
    getStatusByValue(statusEnumValue: string): any {
        return new (RunStatusMap[statusEnumValue as RunStatusEnum])();
    }
}

