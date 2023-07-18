import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { filter, Observable, takeWhile } from 'rxjs';
import { AuthorisedRepo, AuthorisedRepoRelationships } from 'src/app/interfaces/authorised-repo';
import { ProjectWorkspaceVcsConfig } from 'src/app/interfaces/project-workspace-vcs-config';
import { ResponseObjectWithRelationships } from 'src/app/interfaces/response';
import { WorkspaceUpdateAttributes } from 'src/app/interfaces/workspace';
import { ProjectService } from 'src/app/project.service';
import { OrganisationStateType, StateService, WorkspaceStateType } from 'src/app/state.service';
import { WorkspaceService } from 'src/app/workspace.service';

@Component({
  selector: 'app-settings',
  templateUrl: './settings.component.html',
  styleUrls: ['./settings.component.scss']
})
export class SettingsComponent implements OnInit {

  currentOrganisation: Observable<any>;
  currentWorkspace: Observable<any>;
  organisationDetails: any;
  workspaceDetails: any;
  projectDetails: any;
  settingChanges: WorkspaceUpdateAttributes;

  constructor(
    private stateService: StateService,
    private workspaceService: WorkspaceService,
    private projectService: ProjectService,
    private router: Router
  ) {
    this.currentWorkspace = new Observable();
    this.currentOrganisation = new Observable();
    this.workspaceDetails = null;
    this.projectDetails = null;
    this.settingChanges = {
      "file-triggers-enabled": undefined,
      "trigger-patterns": undefined,
      "trigger-prefixes": undefined,
      "vcs-repo": undefined,
      "queue-all-runs": undefined
    };
  }

  onSettingsChange(updates: WorkspaceUpdateAttributes) {
    this.settingChanges = updates;
  }

  onSettingsSave() {
    if (this.workspaceDetails) {
      this.workspaceService.update(
        this.workspaceDetails.data.id,
        this.settingChanges
      ).then((workspaceDetails) => {
        // Update workspace details from response
        this.workspaceDetails = workspaceDetails;
      });
    }
  }

  onChangeVcs(vcsConfig: ProjectWorkspaceVcsConfig) {
    this.workspaceService.update(
      this.workspaceDetails.data.id,
      vcsConfig
    ).then((workspaceDetails) => {
      // Update workspace details from response
      this.workspaceDetails = workspaceDetails;
    });
  }

  ngOnInit(): void {
    this.currentOrganisation = this.stateService.currentOrganisation;
    this.currentWorkspace = this.stateService.currentWorkspace;

    // Subscribe to organisation and workspace state
    this.stateService.currentOrganisation.pipe(filter(v => v.id !== null)).pipe(takeWhile(v => v.id === null, true)).subscribe((currentOrganisation: OrganisationStateType) => {
      this.stateService.currentWorkspace.pipe(filter(v => v.id !== null)).pipe(takeWhile(v => v.id === null, true)).subscribe((currentWorkspace: WorkspaceStateType) => {
        // Get Workspace details and store in member variable
        if (currentOrganisation.name && currentWorkspace.name) {
          let workspaceDetailsSubscription = this.workspaceService.getDetailsByName(currentOrganisation.name, currentWorkspace.name).subscribe((workspaceDetails) => {
            workspaceDetailsSubscription.unsubscribe();

            this.workspaceDetails = workspaceDetails;

            // Obtain details for project
            let projectDetailsSubscription = this.projectService.getDetailsById(this.workspaceDetails.data.relationships.project.data.id).subscribe((projectDetails) => {
              projectDetailsSubscription.unsubscribe();
              this.projectDetails = projectDetails;
            })
          })
        }
      }).unsubscribe();
    }).unsubscribe();
  }
}
