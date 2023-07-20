import { Component, OnInit } from '@angular/core';
import { FormBuilder } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { NbDialogService } from '@nebular/theme';
import { map, Observable } from 'rxjs';
import { ErrorDialogueComponent } from 'src/app/components/error-dialogue/error-dialogue.component';
import { TriggerRunPopupComponent } from 'src/app/components/trigger-run-popup/trigger-run-popup.component';
import { DataItem } from 'src/app/interfaces/data';
import { ResponseObjectWithRelationships } from 'src/app/interfaces/response';
import { RunCreateAttributes } from 'src/app/interfaces/run-create-attributes';
import { WorkspaceAttributes, WorkspaceRelationships } from 'src/app/interfaces/workspace';
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
  tableColumns: string[] = ['icon', 'id', 'commit-message', 'runStatus', 'created-at'];
  workspaceName: string | null = null;
  organisationName: string | null = null;
  workspaceDetails: DataItem<ResponseObjectWithRelationships<WorkspaceAttributes, WorkspaceRelationships>> | null = null;
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
      }, 5000);
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
        this.runService.create(this.currentWorkspace.id, runAttributes).catch((err) => {
          this.dialogService.open(ErrorDialogueComponent, {
            context: {title: err.error.errors?.[0].title, data: err.error.errors?.[0].detail}
          });
        });
      }
    });
  }

  isCurrentRun(row: any): string {
    console.log(row.data.id)
    console.log("vs: " + this.workspaceDetails?.data.relationships['current-run'].data?.id);
    if (this.workspaceDetails?.data.relationships['current-run'].data?.id == row.data.id) {
      return "active-run";
    }
    return "";
  }

  updateRuns(): void {
    if (this.currentWorkspace?.id) {
      let workspaceDataSubscription = this.workspaceService.getDetailsById(this.currentWorkspace?.id).subscribe((data) => {
        workspaceDataSubscription.unsubscribe();
        this.workspaceDetails = data;
      })
    }
    this.runs$ = this.workspaceService.getRuns(this.currentWorkspace?.id || '').pipe(
      map((data) => {
        // Filter includes into configuration versions and ingress attributes
        let configurationVersions = Object.fromEntries(data.included.filter((val: any) => {
          return val['type'] == 'configuration-versions'}
        ).map((val: any) => [val['id'], val]));
        let ingressAttributes = Object.fromEntries(data.included.filter((val: any) => {
          return val['type'] == 'ingress-attributes'}
        ).map((val: any) => [val['id'], val]));

        data.data = data.data.sort((a, b) => {
          return new Date(b.attributes['created-at']).getTime() - new Date(a.attributes['created-at']).getTime()
        })

        return Array.from({length: data.data.length},
          (_, n) => ({'data': {
            id: data.data[n].id,
            runStatus: this.runStatusFactory.getStatusByValue(data.data[n].attributes.status),
            // Obtain related configuration version and ingress attribute for run
            configurationVersion: configurationVersions[data.data[n].relationships['configuration-version']?.data?.id],
            ingressAttribute: ingressAttributes[configurationVersions[data.data[n].relationships['configuration-version']?.data?.id]?.relationships['ingress-attributes']?.data?.id],
            ...data.data[n].attributes
          }})
        )
      })
    );
  }

  ngOnInit(): void {
  }

  onWorkspaceClick(target: any) {
    this.router.navigateByUrl(`/${this.currentOrganisation?.id}/${this.currentWorkspace?.name}/runs/${target.data.id}`)
  }
}
