import { Component, OnInit } from '@angular/core';
import { FormBuilder } from '@angular/forms';
import { Router } from '@angular/router';
import { NbDialogService } from '@nebular/theme';
import { Observable, concat, filter, takeWhile } from 'rxjs';
import { ErrorDialogueComponent } from 'src/app/components/error-dialogue/error-dialogue.component';
import { TriggerRunPopupComponent } from 'src/app/components/trigger-run-popup/trigger-run-popup.component';
import { AuthorisedRepo, AuthorisedRepoRelationships } from 'src/app/interfaces/authorised-repo';
import { ConfigurationVersionAttributes, ConfigurationVersionRelationships } from 'src/app/interfaces/configuration-version';
import { IngressAttributeAttribues } from 'src/app/interfaces/ingress-attribute';
import { OauthClient } from 'src/app/interfaces/oauth-client';
import { ProjectAttributes } from 'src/app/interfaces/project';
import { ProjectWorkspaceVcsConfig } from 'src/app/interfaces/project-workspace-vcs-config';
import { ResponseObject, ResponseObjectWithRelationships, TypedResponseObject, TypedResponseObjectWithRelationships } from 'src/app/interfaces/response';
import { RunAttributes, RunRelationships } from 'src/app/interfaces/run';
import { RunCreateAttributes } from 'src/app/interfaces/run-create-attributes';
import { RunStatusFactory } from 'src/app/models/RunStatus/run-status-factory';
import { OrganisationService } from 'src/app/organisation.service';
import { ProjectService } from 'src/app/project.service';
import { RunService } from 'src/app/run.service';
import { OauthTokenService } from 'src/app/services/oauth-token.service';
import { OrganisationStateType, ProjectStateType, StateService } from 'src/app/state.service';
import { WorkspaceService } from 'src/app/workspace.service';

@Component({
  selector: 'app-overview',
  templateUrl: './overview.component.html',
  styleUrls: ['./overview.component.scss']
})
export class OverviewComponent implements OnInit {

  currentProjectObv: Observable<any>;
  currentOrganisationObv: Observable<any>;
  currentOrganisation: OrganisationStateType;
  workspaceList: string[];
  workspaces: Map<string, Observable<any>>;
  organisationDetails: any;
  projectDetails: any;

  ingressAttributes: {[index: string]: ResponseObject<IngressAttributeAttribues>};
  workspaceRuns: {[index: string]: ResponseObjectWithRelationships<RunAttributes, RunRelationships>};
  configurationVersionIngressAttributes: {[index: string]: string};
  ingressAttributesRuns: {[index: string]: {[index: string]: ResponseObjectWithRelationships<RunAttributes, RunRelationships>}};

  generalSettingsForm = this.formBuilder.group({});
  generalSettingsExecutionMode: string|null;
  generalSettingsTerraformVersion: string;
  _runUpdateInterval: any;

  constructor(
    private stateService: StateService,
    private projectService: ProjectService,
    private workspaceService: WorkspaceService,
    private router: Router,
    private formBuilder: FormBuilder,
    private runStatusFactory: RunStatusFactory,
    private dialogService: NbDialogService,
    private runService: RunService,
  ) {
    this.currentProjectObv = new Observable();
    this.currentOrganisationObv = new Observable();
    this.currentOrganisation = {name: null, id: null};
    this.projectDetails = null;
    this.workspaceList = [];
    this.workspaces = new Map<string, Observable<any>>();
    this.generalSettingsTerraformVersion = "";
    this.generalSettingsExecutionMode = null;
    this.ingressAttributes = {};
    this.workspaceRuns = {};
    this.configurationVersionIngressAttributes = {};
    this.ingressAttributesRuns = {};
    this._runUpdateInterval = null;
  }

  onWorkspaceClick(workspaceId: string): void {
    this.workspaces.get(workspaceId)?.subscribe((data) => {
      this.router.navigateByUrl(`/${this.stateService.currentOrganisation.value?.name}/${data.data.attributes.name}`);
    });
  }

  onChangeVcs(vcsConfig: ProjectWorkspaceVcsConfig) {
    this.projectService.update(
      this.projectDetails.data.id,
      vcsConfig
    ).then((projectDetails) => {
      // Update project details from response
      this.projectDetails = projectDetails;
    })
  }

  onProjectAttributesChange(value: ProjectAttributes): void {
    if (this.projectDetails) {
      this.projectDetails.data.attributes = value;
    }
  }

  onGeneralSettingsSubmit() {
    if (this.projectDetails?.data.id) {
      this.projectService.update(
        this.projectDetails.data.id,
        {
          ...this.projectDetails.data.attributes,
          "execution-mode": this.generalSettingsExecutionMode,
          "terraform-version": this.generalSettingsTerraformVersion
        }
      ).then((projectDetails) => {
        this.projectDetails = projectDetails;
      });
    }
  }

  getIngressAttributesIds(): string[] {
    return Object.keys(this.ingressAttributes).sort((a, b) => 
      (new Date(this.ingressAttributes[b].attributes['created-at']).getTime()) - (new Date(this.ingressAttributes[a].attributes['created-at']).getTime())
    )
  }

  ngOnInit(): void {
    this.currentOrganisationObv = this.stateService.currentOrganisation;
    this.currentProjectObv = this.stateService.currentProject;
    this.workspaceList = [];
    this.workspaces = new Map<string, Observable<any>>();

    this.stateService.currentOrganisation.pipe(filter(v => v.id !== null)).pipe(takeWhile(v => v.id === null, true)).subscribe((currentOrganisation: OrganisationStateType) => {
      if (!currentOrganisation.id) {
        return;
      }

      this.stateService.currentProject.pipe(filter(v => v.id !== null)).pipe(takeWhile(v => v.id === null, true)).subscribe((currentProject: ProjectStateType) => {
        if (!currentProject.name) {
          return;
        }

        // Get list of environments from project details
        if (currentOrganisation.name && currentProject.name) {
          this.currentOrganisation = currentOrganisation;
          let projectSubscription = this.projectService.getDetailsByName(currentOrganisation.name, currentProject.name).subscribe((projectDetails) => {
            projectSubscription.unsubscribe();

            this.projectDetails = projectDetails;

            let workspaces = projectDetails.data.relationships.workspaces.data;

            // Update general settings form
            this.generalSettingsExecutionMode = this.projectDetails.data.attributes['setting-overwrites']['execution-mode']
            this.generalSettingsTerraformVersion = this.projectDetails.data.attributes['terraform-version'];

            // Sort workspaces by order
            workspaces.sort((a: any, b: any) => {
              return a.order > b.order;
            });

            // Obtain workspace details and place into workspaces
            for (let workspace of workspaces) {
              this.workspaceList.push(workspace.id);
              this.workspaces.set(workspace.id, this.workspaceService.getDetailsById(workspace.id));
            }

            // Obtain runs and related ingress attributes for workspaces
            this.updateRunList();
          });
        }
      }).unsubscribe();
    }).unsubscribe();
  }

  ngOnDestroy() {
    if (this._runUpdateInterval) {
      window.clearTimeout(this._runUpdateInterval);
    }
    // Set to false to indicate that runUpdate shouldn't scheduled a new run
    this._runUpdateInterval = false;
  }

  timestampToRelative(timestamp: string): string {
    var d = new Date(timestamp);
    var msPerMinute = 60 * 1000;
    var msPerHour = msPerMinute * 60;
    var msPerDay = msPerHour * 24;
    var msPerMonth = msPerDay * 30;
    var msPerYear = msPerDay * 365;

    let now = new Date();
    var elapsed = now.getTime() - d.getTime();

    if (elapsed < msPerMinute) {
         return Math.round(elapsed/1000) + ' seconds ago';
    }

    else if (elapsed < msPerHour) {
         return Math.round(elapsed/msPerMinute) + ' minutes ago';
    }

    else if (elapsed < msPerDay ) {
         return Math.round(elapsed/msPerHour ) + ' hours ago';
    }

    else if (elapsed < msPerMonth) {
        return '~' + Math.round(elapsed/msPerDay) + ' days ago';
    }

    else if (elapsed < msPerYear) {
        return '~' + Math.round(elapsed/msPerMonth) + ' months ago';
    }

    else {
        return '~' + Math.round(elapsed/msPerYear ) + ' years ago';
    }
  }

  getRunStatusIcon(status: string): string {
    return this.runStatusFactory.getStatusByValue(status).getIcon()
  }

  getRunStatusName(status: string): string {
    return this.runStatusFactory.getStatusByValue(status).getName()
  }

  getRunClass(ingressAttributeId: string, workspaceId: string): string {
    if (this.ingressAttributesRuns[ingressAttributeId] && this.ingressAttributesRuns[ingressAttributeId][workspaceId]) {
      return `run-status-${this.runStatusFactory.getStatusByValue(this.ingressAttributesRuns[ingressAttributeId][workspaceId].attributes.status).getColor()}`;
    }
    return 'run-status-not-run';
  }

  onRunClick(ingressAttributeId: string, workspaceId: string): void {
    // Check if a run exists
    if (this.ingressAttributesRuns[ingressAttributeId] && this.ingressAttributesRuns[ingressAttributeId][workspaceId]) {
      // If so, navigate to run
      this.navigateToRun(ingressAttributeId, workspaceId);
    } else {
      // Otherwise, attempt to create a run
      this.createRunForIngressAttributeAndWorkspace(ingressAttributeId, workspaceId);
    }
  }

  navigateToRun(ingressAttributeId: string, workspaceId: string): void {
    if (this.ingressAttributesRuns[ingressAttributeId] && this.ingressAttributesRuns[ingressAttributeId][workspaceId]) {
      let run = this.ingressAttributesRuns[ingressAttributeId][workspaceId];
      let workspaceSubscription = this.workspaces.get(run.relationships.workspace.data.id)?.subscribe((workspace) => {
        workspaceSubscription?.unsubscribe();
        this.router.navigateByUrl(`/${this.currentOrganisation?.id}/${workspace.data.attributes.name}/runs/${run.id}`)
      });
    }
  }

  async updateRunList(): Promise<void> {
    let runObservables = this.workspaceList.map((workspaceId) => {return this.workspaceService.getRuns(workspaceId)});

    var observable = concat(...runObservables);
    let subscriptionCount = 0;
    let observableSubscription = observable.subscribe((value) => {
      // Unsubscribe from subscription once all subscriptions have been handled.
      subscriptionCount ++;
      if (subscriptionCount == runObservables.length) {
        observableSubscription.unsubscribe();
      }

      value.included.forEach((include) => {
        if (include.type == "ingress-attributes") {
          this.ingressAttributes[include.id] = include;
        }
      });

      value.included.forEach((include) => {
        if (include.type == "configuration-versions" && include.relationships['ingress-attributes'].data) {
          this.configurationVersionIngressAttributes[include.id] = include.relationships['ingress-attributes'].data.id;
        }
      })

      value.data.forEach((run) => {
        let configurationVersionId = run.relationships['configuration-version'].data.id;
        let ingressAttributesId = this.configurationVersionIngressAttributes[configurationVersionId];
        if (ingressAttributesId) {
          // Create mapping for run data based on ingress attribute ID and workspace ID
          if (this.ingressAttributesRuns[ingressAttributesId] === undefined) {
            this.ingressAttributesRuns[ingressAttributesId] = {};
          }
          this.ingressAttributesRuns[ingressAttributesId][run.relationships.workspace.data.id] = run;
        }
      });
    });

    // Obtain ingress attributes for project, for any ingress attributes that don't have
    // a run associated to a workspace
    if (this.projectDetails) {
      let ingressAttributeSubscription = this.projectService.getIngressAttributes(this.projectDetails.data.id).subscribe((ingressAttributes) => {
        ingressAttributeSubscription.unsubscribe();

        ingressAttributes.data.forEach((ingressAttribute) => {
          this.ingressAttributes[ingressAttribute.id] = ingressAttribute;
        })
      });
    }

    if (this._runUpdateInterval !== false) {
      this._runUpdateInterval = setTimeout(() => {this.updateRunList();}, 5000);
    }
  }

  createRunForIngressAttributeAndWorkspace(ingressAttributeId: string, workspaceId: string) {
    // Create pop-up for new run.
    this.dialogService.open(TriggerRunPopupComponent, {
      context: {canDestroy: true}
    }).onClose.subscribe((runAttributes: RunCreateAttributes | null) => {

      // Obtain configuration version based on commit sha
      let commitSha = this.ingressAttributes[ingressAttributeId]?.attributes['commit-sha'];

      if (!commitSha) {
        // Notify user that ingress attributes does not exist
        this.dialogService.open(ErrorDialogueComponent, {
          context: {title: "Error creating run", data: "Could not find git commit for this ingress attribute."}
        });
        return;
      }

      // Obtain configuration version using commit sha
      let configurationVersionSubscription = this.workspaceService.getConfigurationVersionByCommit(workspaceId, commitSha).subscribe((configurationVersionResponse) => {
        configurationVersionSubscription.unsubscribe();

        if (configurationVersionResponse.data.length == 0) {
          // Notify user that configuration version could not be found for commit
          this.dialogService.open(ErrorDialogueComponent, {
            context: {title: "Error creating run", data: "A configuration version for this ingress attribute could not be found for the workspace."}
          });
          return;
        }

        // If the user has triggered the run and a configuration version exists for the workspace for this ingress attribute...
        if (runAttributes) {
          // Create a run for the workspace and configuration version
          this.runService.create(
            workspaceId,
            runAttributes,
            configurationVersionResponse.data[0].id
          ).then((runData) => {
            // Redirect user to new run
            if (this.currentOrganisation) {
              let workspaceSubscription = this.workspaces.get(workspaceId)?.subscribe((workspaceData) => {
                if (workspaceData) {
                  workspaceSubscription?.unsubscribe();
                  this.router.navigateByUrl(`/${this.currentOrganisation.id}/${workspaceData.data.attributes.name}/runs/${runData.data.id}`)
                }
              })
            }
          }).catch((err) => {
            this.dialogService.open(ErrorDialogueComponent, {
              context: {title: err.error.errors?.[0].title, data: err.error.errors?.[0].detail}
            });
          });
        }
      })
    });
  }
}
