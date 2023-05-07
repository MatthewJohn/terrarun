import { Component, OnInit } from '@angular/core';
import { FormBuilder } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { NbDialogService } from '@nebular/theme';
import { map, Observable } from 'rxjs';
import { TriggerRunPopupComponent } from 'src/app/components/trigger-run-popup/trigger-run-popup.component';
import { RunCreateAttributes } from 'src/app/interfaces/run-create-attributes';
import { RunStatusFactory } from 'src/app/models/RunStatus/run-status-factory';
import { RunService } from 'src/app/run.service';
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
              private runStatusFactory: RunStatusFactory,
              private dialogService: NbDialogService,
              private runService: RunService) {
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

  openTriggerRunDialogue() {
    this.dialogService.open(TriggerRunPopupComponent, {
      context: {canDestroy: true}
    }).onClose.subscribe((runAttributes: RunCreateAttributes | null) => {
      if (runAttributes && this.currentWorkspace?.id) {
        this.runService.create(this.currentWorkspace.id, runAttributes);
      }
    });
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
