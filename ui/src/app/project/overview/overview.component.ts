import { Component, OnInit } from '@angular/core';
import { FormBuilder } from '@angular/forms';
import { Router } from '@angular/router';
import { map, Observable, concat } from 'rxjs';
import { AuthorisedRepo, AuthorisedRepoRelationships } from 'src/app/interfaces/authorised-repo';
import { ConfigurationVersionAttributes, ConfigurationVersionRelationships } from 'src/app/interfaces/configuration-version';
import { IngressAttributeAttribues } from 'src/app/interfaces/ingress-attribute';
import { OauthClient } from 'src/app/interfaces/oauth-client';
import { ProjectWorkspaceVcsConfig } from 'src/app/interfaces/project-workspace-vcs-config';
import { ResponseObject, ResponseObjectWithRelationships, TypedResponseObject, TypedResponseObjectWithRelationships } from 'src/app/interfaces/response';
import { RunAttributes, RunRelationships } from 'src/app/interfaces/run';
import { OrganisationService } from 'src/app/organisation.service';
import { ProjectService } from 'src/app/project.service';
import { OauthTokenService } from 'src/app/services/oauth-token.service';
import { OrganisationStateType, ProjectStateType, StateService } from 'src/app/state.service';
import { WorkspaceService } from 'src/app/workspace.service';

@Component({
  selector: 'app-overview',
  templateUrl: './overview.component.html',
  styleUrls: ['./overview.component.scss']
})
export class OverviewComponent implements OnInit {

  currentOrganisation: Observable<any>;
  currentProject: Observable<any>;
  workspaceList: string[];
  workspaces: Map<string, Observable<any>>;
  organisationDetails: any;
  projectDetails: any;

  ingressAttributes: {[index: string]: ResponseObject<IngressAttributeAttribues>};
  workspaceRuns: {[index: string]: ResponseObjectWithRelationships<RunAttributes, RunRelationships>};
  configurationVersionIngressAttributes: {[index: string]: string};

  generalSettingsForm = this.formBuilder.group({
    executionMode: ''
  });

  generalSettingsTerraformVersion: string;

  constructor(
    private stateService: StateService,
    private projectService: ProjectService,
    private workspaceService: WorkspaceService,
    private router: Router,
    private formBuilder: FormBuilder
  ) {
    this.currentProject = new Observable();
    this.currentOrganisation = new Observable();
    this.projectDetails = null;
    this.workspaceList = [];
    this.workspaces = new Map<string, Observable<any>>();
    this.generalSettingsTerraformVersion = "";
    this.ingressAttributes = {};
    this.workspaceRuns = {};
    this.configurationVersionIngressAttributes = {};
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

  onGeneralSettingsSubmit() {
    if (this.projectDetails?.data.id) {
      this.projectService.update(
        this.projectDetails.data.id,
        {
          "execution-mode": this.generalSettingsForm.value.executionMode,
          "terraform-version": this.generalSettingsTerraformVersion
        }
      ).then((projectDetails) => {
        this.projectDetails = projectDetails;
      });
    }
  }

  ngOnInit(): void {
    this.currentOrganisation = this.stateService.currentOrganisation;
    this.currentProject = this.stateService.currentProject;
    this.workspaceList = [];
    this.workspaces = new Map<string, Observable<any>>();

    this.stateService.currentOrganisation.subscribe((currentOrganisation: OrganisationStateType) => {

      this.stateService.currentProject.subscribe((currentProject: ProjectStateType) => {
        // Get list of environments from project details
        if (currentOrganisation.name && currentProject.name) {
          this.projectService.getDetailsByName(currentOrganisation.name, currentProject.name).subscribe((projectDetails) => {

            this.projectDetails = projectDetails;

            let workspaces = projectDetails.data.relationships.workspaces.data;

            // Update general settings form
            this.generalSettingsForm.setValue({
              executionMode: this.projectDetails.data.attributes['execution-mode']
            });
            this.generalSettingsTerraformVersion = this.projectDetails.data.attributes['terraform-version'];

            // Sort workspaces by order
            workspaces.sort((a: any, b: any) => {
              return a.order > b.order;
            });

            // Obtain workspace details and place into workspaces
            for (let workspace of workspaces) {
              this.workspaceList.push(workspace.id);
              this.workspaces.set(workspace.id, this.workspaceService.getDetailsById(workspace.id));
              // this.workspaceService.getDetailsById(workspace.id).subscribe((workspaceDetails) => {
              //   this.workspaces.set(workspaceDetails.data.id, workspaceDetails);
              // });
            }

            // Obtain runs and related ingress attributes for workspaces
            this.updateRunList();
          })
        }
      })
    })
  }

  async updateRunList(): Promise<void> {
    let runObservables = this.workspaceList.map((workspaceId) => {return this.workspaceService.getRuns(workspaceId)});
    let runs: ResponseObjectWithRelationships<RunAttributes, RunRelationships>[] = [];
    let ingressAttributes: TypedResponseObject<"ingress-attributes", IngressAttributeAttribues>[] = [];
    let configurationVersions: TypedResponseObjectWithRelationships<"configuration-versions", ConfigurationVersionAttributes, ConfigurationVersionRelationships>[] = [];

    var observable = concat(...runObservables);
    observable.subscribe((value) => {
      value.data.forEach((run) => {this.workspaceRuns[run.relationships.workspace.data.id]});
      value.included.forEach((include) => {if (include.type == "ingress-attributes") ingressAttributes.push(include)});
      value.included.forEach((include) => {if (include.type == "configuration-versions") configurationVersions.push(include)});

      value.included.forEach((include) => {
        if (include.type == "ingress-attributes") {
          this.ingressAttributes[include.id] = include;
        }
      });

    });
  }
}
