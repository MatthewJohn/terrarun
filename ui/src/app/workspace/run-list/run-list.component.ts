import { Component, OnInit } from '@angular/core';
import { FormBuilder } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { map, Observable } from 'rxjs';
import { RunStatusFactory } from 'src/app/models/RunStatus/run-status-factory';
import { OrganisationStateType, StateService, WorkspaceStateType } from 'src/app/state.service';
import { WorkspaceService } from 'src/app/workspace.service';

@Component({
  selector: 'app-run-list',
  templateUrl: './run-list.component.html',
  styleUrls: ['./run-list.component.scss']
})
export class RunListComponent implements OnInit {

  runs$: Observable<any> | null = null;
  tableColumns: string[] = ['icon', 'id', 'runStatus', 'created-at'];
  workspaceName: string | null = null;
  organisationName: string | null = null;
  _updateInterval: any;


  currentOrganisation: OrganisationStateType | null = null;
  currentWorkspace: WorkspaceStateType | null = null;

  constructor(private state: StateService,
              private workspaceService: WorkspaceService,
              private router: Router,
              private route: ActivatedRoute,
              private formBuilder: FormBuilder,
              private runStatusFactory: RunStatusFactory) {
    this.state.currentWorkspace.subscribe((data) => {
      this.currentWorkspace = data;
      this.updateRuns();
      this._updateInterval = setInterval(() => {
        this.updateRuns();
      }, 1000);
    });

    this.state.currentOrganisation.subscribe((data) => this.currentOrganisation = data);
  }
  ngOnDestroy() {
    if (this._updateInterval) {
      window.clearTimeout(this._updateInterval);
    }
  }

  updateRuns(): void {
    this.runs$ = this.workspaceService.getRuns(this.currentWorkspace?.id || '').pipe(
      map((data) => {
        return Array.from({length: data.data.length},
          (_, n) => ({'data': {
            id: data.data[n].id,
            runStatus: this.runStatusFactory.getStatusByValue(data.data[n].attributes.status),
            ...data.data[n].attributes}}))
      })
    );
  }

  ngOnInit(): void {
  }


  onWorkspaceClick(target: any) {
    this.router.navigateByUrl(`/${this.currentOrganisation?.id}/${this.currentWorkspace?.name}/runs/${target.data.id}`)
  }

}
