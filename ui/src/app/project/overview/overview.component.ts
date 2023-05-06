import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { Observable } from 'rxjs';
import { AuthorisedRepo, AuthorisedRepoRelationships } from 'src/app/interfaces/authorised-repo';
import { OauthClient } from 'src/app/interfaces/oauth-client';
import { ResponseObject, ResponseObjectWithRelationships } from 'src/app/interfaces/response';
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
  organisationOauthClients: any[];
  organisationDetails: any;
  projectDetails: any;
  selectedOauthClient: any | null;

  // Whether the user has started to attach to a new repo
  selectAnotherRepo: boolean;

  // List of authorised reposities from selected oauth token
  authorisedRepos: ResponseObjectWithRelationships<AuthorisedRepo, AuthorisedRepoRelationships>[];

  constructor(
    private stateService: StateService,
    private projectService: ProjectService,
    private workspaceService: WorkspaceService,
    private organisationService: OrganisationService,
    private oauthTokenService: OauthTokenService,
    private router: Router
  ) {
    this.currentProject = new Observable();
    this.organisationOauthClients = [];
    this.currentOrganisation = new Observable();
    this.projectDetails = null;
    this.workspaceList = [];
    this.workspaces = new Map<string, Observable<any>>();
    this.selectedOauthClient = null;
    this.authorisedRepos = [];
    this.selectAnotherRepo = false;
  }

  onWorkspaceClick(workspaceId: string): void {
    this.workspaces.get(workspaceId)?.subscribe((data) => {
      this.router.navigateByUrl(`/${this.stateService.currentOrganisation.value?.name}/${data.data.attributes.name}`);
    });
  }

  onOauthClientSelect(oauthClient: any) {
    this.selectedOauthClient = oauthClient;
    if (oauthClient?.relationships['oauth-tokens'].data && oauthClient.relationships['oauth-tokens'].data[0].id) {
      this.oauthTokenService.getAuthorisedRepos(oauthClient.relationships['oauth-tokens'].data[0].id).then((data) => {
        this.authorisedRepos = data;
      });
    } else {
      // Otherwise, clear list of repos
      this.authorisedRepos = [];
    }
  }

  onSelectAnotherRepo() {
    this.selectAnotherRepo = true;
  }

  onSelectRepository(authorisedRepo: ResponseObjectWithRelationships<AuthorisedRepo, AuthorisedRepoRelationships> | null) {
    this.projectService.update(
      this.projectDetails.data.id,
      {
        "vcs-repo": {
          "identifier": authorisedRepo ? authorisedRepo.attributes.name : null,
          "oauth-token-id": authorisedRepo ? authorisedRepo.relationships['oauth-token'].data.id : null
        }
      }
    ).then((projectDetails) => {
      // Update project details from response
      this.projectDetails.data = projectDetails;

      // Reset data for selecting VCS provider etc.
      this.selectAnotherRepo = false;
      this.selectedOauthClient = null;
      this.authorisedRepos = [];
    })
  }

  ngOnInit(): void {
    this.currentOrganisation = this.stateService.currentOrganisation;
    this.currentProject = this.stateService.currentProject;
    this.workspaceList = [];
    this.workspaces = new Map<string, Observable<any>>();

    this.stateService.currentOrganisation.subscribe((currentOrganisation: OrganisationStateType) => {

      if (currentOrganisation.name) {
        this.organisationService.getOrganisationOauthClients(currentOrganisation.name).then((data) => {
          this.organisationOauthClients = data.filter((val: any) => val.relationships["oauth-tokens"].data.length);
        })
      }

      this.stateService.currentProject.subscribe((currentProject: ProjectStateType) => {
        // Get list of environments from project details
        if (currentOrganisation.name && currentProject.name) {
          this.projectService.getDetailsByName(currentOrganisation.name, currentProject.name).subscribe((projectDetails) => {

            this.projectDetails = projectDetails;

            let workspaces = projectDetails.data.relationships.workspaces.data;

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
          })
        }
      })
    })
  }

}
