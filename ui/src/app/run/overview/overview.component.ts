import { Component, OnInit, ViewEncapsulation } from '@angular/core';
import { ActivatedRoute, Route, RouterModule } from '@angular/router';
import { ApplyService } from 'src/app/apply.service';
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

  _runDetails: any;
  _planDetails: any;
  _applyDetails: any;
  _planLog: string;
  _applyLog: string;
  _runStatus: any;
  _createdByDetails: any;

  constructor(private route: ActivatedRoute,
              private runService: RunService,
              private planService: PlanService,
              private applyService: ApplyService,
              private userService: UserService,
              private runStatusFactory: RunStatusFactory) {
    this._planLog = "";
    this._applyLog = "";
  }

  ngOnInit(): void {
    this.route.paramMap.subscribe((routeParams) => {
      let runId = routeParams.get('runId');
      if (runId) {
        this.runService.getDetailsById(runId).subscribe((runData) => {
          this._runDetails = runData.data;

          // Obtain run status model
          this._runStatus = this.runStatusFactory.getStatusByValue(this._runDetails.attributes.status);

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
              this.planService.getLog(this._planDetails.attributes['log-read-url']).subscribe((planLog) => {this._planLog = planLog;})
            })
          }

          // Obtain apply details
          if (this._runDetails.relationships.apply) {
            this.applyService.getDetailsById(this._runDetails.relationships.apply.data.id).subscribe((applyData) => {
              this._applyDetails = applyData.data;
              this.applyService.getLog(this._applyDetails.attributes['log-read-url']).subscribe((applyLog) => {this._applyLog = applyLog;})
            })
          }
        });
      }
    });
  }
}
