export enum RunStatusEnum {
    PENDING = "pending",
    FETCHING = "fetching",
    QUEUING = "queuing",
    PLAN_QUEUED = "plan_queued",
    PLANNING = "planning",
    PLANNED = "planned",
    COST_ESTIMATING = "cost_estimating",
    COST_ESTIMATED = "cost_estimated",
    POLICY_CHECKING = "policy_checking",
    POLICY_OVERRIDE = "policy_override",
    POLICY_SOFT_FAILED = "policy_soft_failed",
    POLICY_CHECKED = "policy_checked",
    CONFIRMED = "confirmed",
    POST_PLAN_RUNNING = "post_plan_running",
    POST_PLAN_COMPLETED = "post_plan_completed",
    PLANNED_AND_FINISHED = "planned_and_finished",
    APPLY_QUEUED = "apply_queued",
    APPLYING = "applying",
    APPLIED = "applied",
    DISCARDED = "discarded",
    ERRORED = "errored",
    CANCELED = "canceled",
    FORCE_CANCELLED = "force_canceled"
}
