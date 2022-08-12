import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Route, RouterModule } from '@angular/router';
import { ApplyService } from 'src/app/apply.service';
import { PlanService } from 'src/app/plan.service';
import { RunService } from 'src/app/run.service';

@Component({
  selector: 'app-overview',
  templateUrl: './overview.component.html',
  styleUrls: ['./overview.component.scss']
})
export class OverviewComponent implements OnInit {

  _runDetails: any;
  _planDetails: any;
  _applyDetails: any;

  constructor(private route: ActivatedRoute,
              private runService: RunService,
              private planService: PlanService,
              private applyService: ApplyService) { }

  ngOnInit(): void {
    this.route.paramMap.subscribe((routeParams) => {
      let runId = routeParams.get('runId');
      if (runId) {
        this.runService.getDetailsById(runId).subscribe((runData) => {
          this._runDetails = runData.data;

          if (this._runDetails.relationships.plan) {
            this.planService.getDetailsById(this._runDetails.relationships.plan.data.id).subscribe((planData) => {
              this._planDetails = planData.data;
              console.log(this._planDetails);
            })
          }

          if (this._runDetails.relationships.apply) {
            this.applyService.getDetailsById(this._runDetails.relationships.apply.data.id).subscribe((applyData) => {
              this._applyDetails = applyData.data;
            })
          }
        });
      }
    });
  }

}
