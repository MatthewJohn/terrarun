import { Component, OnInit, ViewEncapsulation } from '@angular/core';
import { ActivatedRoute, Route, RouterModule } from '@angular/router';
import { Observable, Subscription } from 'rxjs';
import { ApplyService } from 'src/app/apply.service';
import { PlanApplyStatusFactory } from 'src/app/models/PlanApplyStatus/plan-apply-status-factory';
import { RunAction } from 'src/app/models/RunAction/run-action-enum';
import { RunStatusFactory } from 'src/app/models/RunStatus/run-status-factory';
import { TaskStage } from 'src/app/models/TaskStage/task-stage';
import { PlanService } from 'src/app/plan.service';
import { RunService } from 'src/app/run.service';
import { TaskResultService } from 'src/app/task-result.service';
import { TaskStageService } from 'src/app/task-stage.service';
import { UserService } from 'src/app/user.service';

@Component({
  selector: 'app-overview',
  templateUrl: './overview.component.html',
  styleUrls: ['./overview.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class OverviewComponent implements OnInit {

  _runId: string | null = null;
  _runDetails: any;
  _runStatus: any;

  _planDetails: any;
  _planLog: string;
  _planStatus: any;
  _applyDetails: any;
  _applyLog: string;
  _applyStatus: any;
  _auditEvents: any;

  // Whether the state has changed between
  _stateChanged: boolean;
  _previousRunStatus: string | null;
  _knownTaskStages: string[] = [];

  _prePlanTaskStage: any;
  _postPlanTaskStage: any;
  _preApplyTaskStage: any;
    
  _createdByDetails: any;
  _updateInterval: any;
  _prePlanTaskResults$: Observable<any>;

  constructor(private route: ActivatedRoute,
              private runService: RunService,
              private planService: PlanService,
              private applyService: ApplyService,
              private userService: UserService,
              private runStatusFactory: RunStatusFactory,
              private planApplyStatusFactory: PlanApplyStatusFactory,
              private taskStageService: TaskStageService,
              private taskResultService: TaskResultService) {
    this._planLog = "";
    this._applyLog = "";
    this._prePlanTaskStage = undefined;
    this._postPlanTaskStage = undefined;
    this._preApplyTaskStage = undefined;
    this._prePlanTaskResults$ = new Observable();
    this._stateChanged = true;
    this._previousRunStatus = null;
  }

  ngOnInit(): void {
    this.route.paramMap.subscribe((routeParams) => {
      let runId = routeParams.get('runId');
      this._runId = runId;
      this._updateInterval = setInterval(() => {
        this.getRunStatus();
      }, 1000);
      this.getRunStatus();
    });
  }
  ngOnDestroy() {
    if (this._updateInterval) {
      window.clearTimeout(this._updateInterval);
    }
  }

  getRunStatus() {
    if (this._runId) {
      let runSubscription = this.runService.getDetailsById(this._runId).subscribe((runData) => {
        runSubscription.unsubscribe();
        this._runDetails = runData.data;

        this._stateChanged = this._previousRunStatus !== this._runDetails.attributes.status;
        this._previousRunStatus = this._runDetails.attributes.status;

        // Obtain run status model
        this._runStatus = this.runStatusFactory.getStatusByValue(this._runDetails.attributes.status);
        if (this._runStatus.isFinal()) {
          window.clearTimeout(this._updateInterval);
        }

        // Obtain "created by" user details, if not already obtained
        if (this._runDetails.relationships["created-by"]?.data && ! this._createdByDetails) {
          let userSubscription = this.userService.getUserDetailsById(this._runDetails.relationships["created-by"].data.id).subscribe((userDetails) => {
            userSubscription.unsubscribe();
            this._createdByDetails = userDetails.data;
          })
        }

        // Obtain plan details
        if (this._runDetails.relationships.plan && (this._runStatus.shouldCheckPlan() || this._stateChanged)) {
          let planSubscription = this.planService.getDetailsById(this._runDetails.relationships.plan.data.id).subscribe((planData) => {
            planSubscription.unsubscribe();
            this._planDetails = planData.data;
            this._planStatus = this.planApplyStatusFactory.getStatusByValue(this._planDetails.attributes.status);
            this.planService.getLog(this._planDetails.attributes['log-read-url']).subscribe((planLog) => {this._planLog = planLog;})
          })
        }

        // Obtain apply details
        if (this._runDetails.relationships.apply.data !== undefined && (this._runStatus.shouldCheckApply() || this._stateChanged)) {
          let applySubscription = this.applyService.getDetailsById(this._runDetails.relationships.apply.data.id).subscribe((applyData) => {
            applySubscription.unsubscribe();
            this._applyDetails = applyData.data;
            this._applyStatus = this.planApplyStatusFactory.getStatusByValue(this._applyDetails.attributes.status);
            this.applyService.getLog(this._applyDetails.attributes['log-read-url']).subscribe((applyLog) => {this._applyLog = applyLog;})
          })
        }

        // Iterate over plan stages, obtain details and populate in
        // appropriate member variables
        for (let taskStageRelationship of this._runDetails.relationships['task-stages'].data) {

          let taskStageId = taskStageRelationship.id;

          if (
              this._knownTaskStages.indexOf(taskStageId) !== -1 &&
              !this._runStatus.shouldCheckPrePlan() &&
              !this._runStatus.shouldCheckPostPlan() &&
              !this._runStatus.shouldCheckPreApply() &&
              !this._stateChanged) {
            break;
          }

          if (taskStageId) {
            let ts = new TaskStage(taskStageId, this.taskStageService, this.taskResultService);
            let taskStateSubscribe = ts.details$.subscribe((taskStageData) => {
              this._knownTaskStages.push(taskStageId);
              taskStateSubscribe.unsubscribe();
              if (taskStageData.data.attributes.stage == 'pre_plan') {
                if (this._prePlanTaskStage === undefined) {
                  this._prePlanTaskStage = new TaskStage(
                    taskStageData.data.id,
                    this.taskStageService,
                    this.taskResultService);
                  } else if (this._runStatus.shouldCheckPrePlan() || this._stateChanged) {
                    this._prePlanTaskStage.update();
                  }
                // this._prePlanTaskStage = ts;
              } else if (taskStageData.data.attributes.stage == 'post_plan') {
                if (this._postPlanTaskStage === undefined) {
                  this._postPlanTaskStage = new TaskStage(
                    taskStageData.data.id,
                    this.taskStageService,
                    this.taskResultService);
                } else if (this._runStatus.shouldCheckPostPlan() || this._stateChanged) {
                  this._postPlanTaskStage.update();
                }
              } else if (taskStageData.data.attributes.stage == 'pre_apply') {
                if (this._preApplyTaskStage === undefined) {
                  this._preApplyTaskStage = new TaskStage(
                    taskStageData.data.id,
                    this.taskStageService,
                    this.taskResultService);
                } else if (this._runStatus.shouldCheckPreApply() || this._stateChanged) {
                  this._preApplyTaskStage.update();
                }
              }
            })
          }
        }
      });

      // Obtain plan audit events
      this.runService.getAuditEventsByRunId(this._runId).subscribe(async (auditEvents) => {
        let auditEventsArray: object[] = [];

        for (const event of auditEvents.data) {
          if (event.attributes.type == 'status_change') {
            let description = 'Status changed: ' + this.runStatusFactory.getStatusByValue(event.attributes['new-value']).getName();
            let user = 'system';
            if (event.relationships.user.data.id !== undefined) {
              user = (await this.userService.getUserDetailsByIdSync(event.relationships.user.data.id)).data.attributes.username;
            }
            auditEventsArray.push({
              description: description,
              timestamp: new Date(event.attributes.timestamp).toLocaleString(),
              date: new Date(event.attributes.timestamp),
              user: user
            })
          }
        }
        this._auditEvents = auditEventsArray;
      });
    }
  }

  applyActionAvailable(): boolean {
    if (this._runStatus && this._runStatus.getAvailableActions().indexOf(RunAction.CONFIRM_AND_APPLY) !== -1) {
      return true;
    }
    return false;
  }
  applyRun() {
    if (this._runId) {
      this.runService.applyRun(this._runId).subscribe((data) => {
      });
    }
  }
  cancelActionAvailable(): boolean {
    if (this._runStatus && this._runStatus.getAvailableActions().indexOf(RunAction.CANCEL_RUN) !== -1) {
      return true;
    }
    return false;
  }
  cancelRun() {
    if (this._runId) {
      this.runService.cancelRun(this._runId).subscribe((data) => {
      });
    }
  }
  discardActionAvailable(): boolean {
    if (this._runStatus && this._runStatus.getAvailableActions().indexOf(RunAction.DISCARD_RUN) !== -1) {
      return true;
    }
    return false;
  }
  discardRun() {
    if (this._runId) {
      this.runService.discardRun(this._runId).subscribe((data) => {
      });
    }
  }
  retryActionAvailable(): boolean {
    if (this._runStatus && this._runStatus.getAvailableActions().indexOf(RunAction.RETRY_RUN) !== -1) {
      return true;
    }
    return false;
  }
  retryRun() {
    if (this._runId) {
      // @TODO
      // this.runService.retryRun(this._runId).subscribe((data) => {
      // });
    }
  }
}
