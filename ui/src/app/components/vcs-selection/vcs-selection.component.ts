import { Component, Input, OnInit, Output, EventEmitter } from '@angular/core';
import { NbTagComponent, NbTagInputAddEvent } from '@nebular/theme';
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

  @Input()
  parentVcsConfig: ProjectWorkspaceVcsConfig | null = null;

  @Output()
  onChangeVcs: EventEmitter<ProjectWorkspaceVcsConfig> = new EventEmitter();

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

  // Whether branch can be set
  canSetBranch: boolean;

  // Whether triggers can be configured
  canSetTrigger: boolean;

  // Which VCS trigger option has been selected
  selectedTriggerOption: any;

  // List of strings for VCS prefixes and patterns
  selectedPathTriggerType: string;
  triggerPatterns: Set<string>;
  triggerPrefixes: Set<string>;

  // Tag regex
  tagRegex: string | null;

  // Branch name
  branch: string | null;

  constructor(
    private stateService: StateService,
    private oauthTokenService: OauthTokenService,
    private organisationService: OrganisationService
  ) {
    this.selectAnotherRepo = false;
    this.currentOrganisation = null;
    this.organisationOauthClients = [];
    this.authorisedRepos = [];
    this.canSetBranch = false;
    this.canSetTrigger = false;
    this.selectedTriggerOption = null;
    this.triggerPatterns = new Set(this.parentVcsConfig?.['trigger-patterns'] || this.vcsConfig?.['trigger-patterns'] || []);
    this.triggerPrefixes = new Set(this.parentVcsConfig?.['trigger-prefixes'] || this.vcsConfig?.['trigger-prefixes'] || []);

    // Default to all triggers
    this.selectedTriggerOption = 'all';

    this.tagRegex = this.parentVcsConfig?.['vcs-repo']?.['tags-regex'] || this.vcsConfig?.['vcs-repo']?.['tags-regex'] || '';
    if (this.tagRegex) {
      this.selectedTriggerOption = 'tag_trigger';
    }

    // If trigger pattern has been set, default to this
    if (this.triggerPatterns.size) {
      this.selectedPathTriggerType = 'pattern';
      this.selectedTriggerOption = 'file_trigger';
    } else if (this.triggerPrefixes.size) {
      // Otherwise, if prefix has been defined, use this
      this.selectedPathTriggerType = 'prefix';
      this.selectedTriggerOption = 'file_trigger';
    } else {
      // If neiter has been set, default to pattern
      this.selectedPathTriggerType = 'pattern';
    }
    this.branch = this.parentVcsConfig?.['vcs-repo']?.branch || this.vcsConfig?.['vcs-repo']?.branch || '';
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
    });

    this.canSetBranch = this.parentVcsConfig?.['vcs-repo']?.branch ? false : true;
    this.canSetTrigger = ! (
      this.parentVcsConfig?.['vcs-repo']?.['tags-regex'] ||
      this.parentVcsConfig?.['trigger-patterns'] ||
      this.parentVcsConfig?.['trigger-prefixes']
    );
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

  onTriggerPrefixRemove(tagToRemove: NbTagComponent): void {
    this.triggerPrefixes.delete(tagToRemove.text);
  }

  onTriggerPrefixAdd({ value, input }: NbTagInputAddEvent): void {
    if (value) {
      this.triggerPrefixes.add(value)
    }
    input.nativeElement.value = '';
  }

  onTriggerPatternRemove(tagToRemove: NbTagComponent): void {
    this.triggerPatterns.delete(tagToRemove.text);
  }

  onTriggerPatternAdd({ value, input }: NbTagInputAddEvent): void {
    if (value) {
      this.triggerPatterns.add(value)
    }
    input.nativeElement.value = '';
  }

  onUpdateSettings() {
    this.onChangeVcs.emit({
      "vcs-repo": {
        // If the branch can be set, use the user specified branch,
        // defaulting to None if it's empty
        branch: this.canSetBranch ? (this.branch || null) : null,

        // If the tag regex can be set, use the user specified tagregex,
        // defaulting to None if it's empty. Use null if the trigger type
        // has not been set to tags
        "tags-regex": this.selectedTriggerOption == 'tag_trigger' ? (this.canSetTrigger ? (this.tagRegex || null) : null) : null,

        // Do not update the VCS repo
        identifier: undefined,
        "oauth-token-id": undefined,

        "ingress-submodules": undefined,
        "display-identifier": undefined,
        "webhook-url": undefined,
        "repository-http-url": undefined,
        "service-provider": undefined
      },
      "file-triggers-enabled": this.selectedTriggerOption == 'file_trigger',
      // If specifying a file trigger, convert prefix/pattern sets to array.
      // Otherwise provide an empty list
      "trigger-patterns": this.selectedTriggerOption == 'file_trigger' && this.selectedPathTriggerType == 'pattern' ? Array.from(this.triggerPatterns.values()) : [],
      "trigger-prefixes": this.selectedTriggerOption == 'file_trigger' && this.selectedPathTriggerType == 'prefix' ? Array.from(this.triggerPrefixes.values()) : [],
    })
  }

  onSelectRepository(authorisedRepo: ResponseObjectWithRelationships<AuthorisedRepo, AuthorisedRepoRelationships> | null) {
    this.onChangeVcs.emit({
      "vcs-repo": {
        // If the branch can be set, use the user specified branch,
        // defaulting to None if it's empty
        branch: this.canSetBranch ? (this.branch || null) : null,

        // If the tag regex can be set, use the user specified tagregex,
        // defaulting to None if it's empty. Use null if the trigger type
        // has not been set to tags
        "tags-regex": this.selectedTriggerOption == 'tag_trigger' ? (this.canSetTrigger ? (this.tagRegex || null) : null) : null,

        identifier: authorisedRepo ? authorisedRepo.attributes.name : null,
        "oauth-token-id": authorisedRepo ? authorisedRepo.relationships['oauth-token'].data.id : null,

        "ingress-submodules": undefined,
        "display-identifier": undefined,
        "webhook-url": undefined,
        "repository-http-url": undefined,
        "service-provider": undefined
      },
      "file-triggers-enabled": false,
      "trigger-prefixes": [],
      "trigger-patterns": []
    });

    // Reset data for selecting VCS provider etc.
    this.selectAnotherRepo = false;
    this.selectedOauthClient = null;
    this.authorisedRepos = [];
  }
}
