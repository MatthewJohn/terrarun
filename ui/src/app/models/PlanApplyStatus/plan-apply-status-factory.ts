import { Injectable } from "@angular/core";
import { IPlanApplyStatus } from "./plan-apply-status";
import { PlanApplyStatusEnum } from "./plan-apply-status-enum";

abstract class PlanApplyBaseClass implements IPlanApplyStatus {
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

class PlanApplyStatusPending extends PlanApplyBaseClass {
    _nameString = "Pending";
    _labelColour = "basic";
    _icon = "done-all-outline";
}
class PlanApplyStatusManagedQueued extends PlanApplyBaseClass {
    _nameString = "Managed queued";
    _labelColour = "basuc";
    _icon = "done-all-outline";
}
class PlanApplyStatusQueued extends PlanApplyBaseClass {
    _nameString = "Queued";
    _labelColour = "basic";
    _icon = "done-all-outline";
}
class PlanApplyStatusRunning extends PlanApplyBaseClass {
    _nameString = "Running";
    _labelColour = "info";
    _icon = "done-all-outline";
}
class PlanApplyStatusErrored extends PlanApplyBaseClass {
    _nameString = "Errored";
    _labelColour = "danger";
    _icon = "done-all-outline";
}
class PlanApplyStatusCanceled extends PlanApplyBaseClass {
    _nameString = "Canceled";
    _labelColour = "warning";
    _icon = "done-all-outline";
}
class PlanApplyStatusFinished extends PlanApplyBaseClass {
    _nameString = "Finished";
    _labelColour = "success";
    _icon = "done-all-outline";
}
class PlanApplyStatusUnreachable extends PlanApplyBaseClass {
    _nameString = "Unreachable";
    _labelColour = "danger";
    _icon = "done-all-outline";
}

const PlanApplySatusMap: Record<PlanApplyStatusEnum, new (...args: any[]) => IPlanApplyStatus> = {
    [PlanApplyStatusEnum.PENDING]: PlanApplyStatusPending,
    [PlanApplyStatusEnum.MANAGED_QUEUED]: PlanApplyStatusManagedQueued,
    [PlanApplyStatusEnum.QUEUED]: PlanApplyStatusQueued,
    [PlanApplyStatusEnum.RUNNING]: PlanApplyStatusRunning,
    [PlanApplyStatusEnum.ERRORED]: PlanApplyStatusErrored,
    [PlanApplyStatusEnum.CANCELED]: PlanApplyStatusCanceled,
    [PlanApplyStatusEnum.FINISHED]: PlanApplyStatusFinished,
    [PlanApplyStatusEnum.UNREACHABLE]: PlanApplyStatusUnreachable,

}

@Injectable({
    providedIn: 'root'
  })
export class PlanApplyStatusFactory {
    // @TODO Update signure to match instance of 'new (...args: any[]) => IRunStatus)'
    getStatusByValue(statusEnumValue: string): any {
        return new PlanApplySatusMap[statusEnumValue as PlanApplyStatusEnum]();
    }
}
