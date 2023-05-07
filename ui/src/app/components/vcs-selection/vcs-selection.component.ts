import { Component, Input, OnInit, Output, EventEmitter } from '@angular/core';
import { AuthorisedRepo, AuthorisedRepoRelationships } from 'src/app/interfaces/authorised-repo';
import { ProjectWorkspaceVcsConfig } from 'src/app/interfaces/project-workspace-vcs-config';
import { ResponseObjectWithRelationships } from 'src/app/interfaces/response';
import { OrganisationService } from 'src/app/organisation.service';
import { OauthTokenService } from 'src/app/services/oauth-token.service';
import { OrganisationStateType, StateService } from 'src/app/state.service';

@Component({
  selector: 'app-vcs-selection',
  templateUrl: './vcs-selection.component.html',
  styleUrls: ['./vcs-selection.component.scss']
})
export class VcsSelectionComponent implements OnInit {

  @Input()
  vcsConfig: ProjectWorkspaceVcsConfig | null = null;

  @Output()
  onChangeVcs: EventEmitter<ResponseObjectWithRelationships<AuthorisedRepo, AuthorisedRepoRelationships> | null> = new EventEmitter();

  // Whether a change of repo has been selected
  selectAnotherRepo: boolean;

  // Current organisation
  currentOrganisation: OrganisationStateType|null;

  // List of oauth client avaiable to the organisation
  organisationOauthClients: any[];

  // Current selected oauth client
  selectedOauthClient: any | null;

  // List of authorised reposities from selected oauth token
  authorisedRepos: ResponseObjectWithRelationships<AuthorisedRepo, AuthorisedRepoRelationships>[];

  constructor(
    private stateService: StateService,
    private oauthTokenService: OauthTokenService,
    private organisationService: OrganisationService
  ) {
    this.selectAnotherRepo = false;
    this.currentOrganisation = null;
    this.organisationOauthClients = [];
    this.authorisedRepos = [];
  }

  ngOnInit(): void {
    // Subscribe to current organisation
    this.stateService.currentOrganisation.subscribe((currentOrganisation) => {
      // Store current organisation
      this.currentOrganisation = currentOrganisation;

      // Obtain list of oauth clients for organisation
      if (this.currentOrganisation?.name) {
        this.organisationService.getOrganisationOauthClients(this.currentOrganisation.name).then((data) => {
          this.organisationOauthClients = data.filter((val: any) => val.relationships["oauth-tokens"].data.length);
        })
      }
    })
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
    this.onChangeVcs.emit(authorisedRepo);
  }

}
