import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { Observable } from 'rxjs';
import { AuthorisedRepo, AuthorisedRepoRelationships } from 'src/app/interfaces/authorised-repo';
import { ResponseObjectWithRelationships } from 'src/app/interfaces/response';
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

  constructor(
    private stateService: StateService,
    private workspaceService: WorkspaceService,
    private router: Router
  ) {
    this.currentWorkspace = new Observable();
    this.currentOrganisation = new Observable();
    this.workspaceDetails = null;
  }

  onChangeVcs(authorisedRepo: ResponseObjectWithRelationships<AuthorisedRepo, AuthorisedRepoRelationships> | null) {
    this.workspaceService.update(
      this.workspaceDetails.data.id,
      {
        "vcs-repo": {
          "identifier": authorisedRepo ? authorisedRepo.attributes.name : null,
          "oauth-token-id": authorisedRepo ? authorisedRepo.relationships['oauth-token'].data.id : null
        }
      }
    ).then((workspaceDetails) => {
      // Update project details from response
      this.workspaceDetails.data = workspaceDetails;
    })
  }

  ngOnInit(): void {
    this.currentOrganisation = this.stateService.currentOrganisation;
    this.currentWorkspace = this.stateService.currentWorkspace;

    // Subscribe to organisation and workspace state
    this.stateService.currentOrganisation.subscribe((currentOrganisation: OrganisationStateType) => {
      this.stateService.currentWorkspace.subscribe((currentWorkspace: WorkspaceStateType) => {
        // Get Workspace details and store in member variable
        if (currentOrganisation.name && currentWorkspace.name) {
          this.workspaceService.getDetailsByName(currentOrganisation.name, currentWorkspace.name).subscribe((workspaceDetails) => {

            this.workspaceDetails = workspaceDetails;
          })
        }
      })
    })
  }
}
