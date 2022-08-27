import { Component, OnInit, ViewEncapsulation } from '@angular/core';
import { ActivatedRoute, Route, RouterModule } from '@angular/router';
import { ApplyService } from 'src/app/apply.service';
import { PlanApplyStatusFactory } from 'src/app/models/PlanApplyStatus/plan-apply-status-factory';
import { RunAction } from 'src/app/models/RunAction/run-action-enum';
import { RunStatusFactory } from 'src/app/models/RunStatus/run-status-factory';
import { PlanService } from 'src/app/plan.service';
import { RunService } from 'src/app/run.service';
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
    
  _createdByDetails: any;
  _updateInterval: any;

  constructor(private route: ActivatedRoute,
              private runService: RunService,
              private planService: PlanService,
              private applyService: ApplyService,
              private userService: UserService,
              private runStatusFactory: RunStatusFactory,
              private planApplyStatusFactory: PlanApplyStatusFactory) {
    this._planLog = "";
    this._applyLog = "";
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
      this.runService.getDetailsById(this._runId).subscribe((runData) => {
        this._runDetails = runData.data;

        // Obtain run status model
       this._runStatus = this.runStatusFactory.getStatusByValue(this._runDetails.attributes.status);
       if (this._runStatus.isFinal()) {
         window.clearTimeout(this._updateInterval);
       }

        // Obtain "created by" user details
        if (this._runDetails.relationships["created-by"].data) {
          this.userService.getUserDetailsById(this._runDetails.relationships["created-by"].data.id).subscribe((userDetails) => {
            this._createdByDetails = userDetails.data;
          })
        }

        // Obtain plan details
        if (this._runDetails.relationships.plan) {
          this.planService.getDetailsById(this._runDetails.relationships.plan.data.id).subscribe((planData) => {
            this._planDetails = planData.data;
            this._planStatus = this.planApplyStatusFactory.getStatusByValue(this._planDetails.attributes.status);
            this.planService.getLog(this._planDetails.attributes['log-read-url']).subscribe((planLog) => {this._planLog = planLog;})
          })
        }

        // Obtain apply details
        if (this._runDetails.relationships.apply.data !== undefined) {
          this.applyService.getDetailsById(this._runDetails.relationships.apply.data.id).subscribe((applyData) => {
            this._applyDetails = applyData.data;
            this._applyStatus = this.planApplyStatusFactory.getStatusByValue(this._applyDetails.attributes.status);
            this.applyService.getLog(this._applyDetails.attributes['log-read-url']).subscribe((applyLog) => {this._applyLog = applyLog;})
          })
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
        // Sort list of events by the date
        auditEventsArray.sort((a: any, b: any): number => {
          return a.date - b.date
        });
        this._auditEvents = auditEventsArray;
      });
    }
  }

  applyActionAvailable(): boolean {
    if (this._runStatus.getAvailableActions().indexOf(RunAction.CONFIRM_AND_APPLY) !== -1) {
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
    if (this._runStatus.getAvailableActions().indexOf(RunAction.CANCEL_RUN) !== -1) {
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
}
