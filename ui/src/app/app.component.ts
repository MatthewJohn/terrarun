import { Component } from '@angular/core';
import { NbMenuItem, NbSidebarService } from '@nebular/theme';
import { AccountService } from './account.service';
import { HomeComponent } from './home/home.component';
import { AuthenticationStateType, OrganisationStateType, RunStateType, StateService, WorkspaceStateType } from './state.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {

  title = 'ui';
  _authenticationState: AuthenticationStateType = {authenticated: false, id: null, username: null};
  _currentOrganisationState: OrganisationStateType = {id: null, name: null};
  _currentWorkspace: WorkspaceStateType = {id: null, name: null};
  _currentRun: RunStateType = {id: null};
  items: NbMenuItem[] = [];

  constructor(private readonly sidebarService: NbSidebarService,
              private accountService: AccountService,
              private stateService: StateService) {
    this.accountService.getAccountDetails();

    this.stateService.authenticationState.subscribe((data) => {
      this._authenticationState = data;
      this.updateMenuItems();
    });
    this.stateService.currentOrganisation.subscribe((data) => {
      this._currentOrganisationState = data;
      this.updateMenuItems();
    });
    this.stateService.currentWorkspace.subscribe((data) => {
      this._currentWorkspace = data;
      this.updateMenuItems();
    });
    this.stateService.currentRun.subscribe((data) => {
      this._currentRun = data;
      this.updateMenuItems();
    });
  }

  updateMenuItems() {
    if (this._authenticationState.authenticated == true) {
      this.items = [
        {
          title: 'Home',
          link: '/home',
          icon: 'home-outline'
        },
        {
          title: 'Organisations',
          icon: 'globe-outline',
          children: [
            {
              title: 'Create',
              link: '/organisation/create'
            },
            {
              title: 'List',
              link: '/organisation/list'
            }
          ]
        },
        {
          title: 'Settings',
          link: '/settings',
          icon: 'settings-2-outline',
          children: [
            {
              title: 'User Tokens',
              link: '/settings/tokens'
            }
          ]
        }
      ];

      // Add links for current organisation
      if (this._currentOrganisationState.id) {
        this.items.splice(2, 0, {
          title: `Organisation: ${this._currentOrganisationState.name}`,
          link: `/${this._currentOrganisationState.id}`,
          children: [
            {
              title: 'Overview',
              link: `/${this._currentOrganisationState.id}`
            },
            {
              title: 'Workspaces',
              link: `/${this._currentOrganisationState.id}/workspaces`
            },
            {
              title: 'Tasks',
              link: `/${this._currentOrganisationState.id}/tasks`
            },
            {
              title: 'Settings',
              link: `/${this._currentOrganisationState.id}/settings`
            }
          ]
        });
        if (this._currentWorkspace.id) {
          this.items.splice(3, 0, {
            title: `Workspace: ${this._currentWorkspace.name}`,
            link: `/${this._currentOrganisationState.id}/${this._currentWorkspace.name}`,
            children: [
              {
                title: 'Runs',
                link: `/${this._currentOrganisationState.id}/${this._currentWorkspace.name}/runs`
              }
            ]
          })
        }
        if (this._currentRun.id) {
          this.items.splice(4, 0, {
            title: `Run: ${this._currentRun.id}`,
            link: `/${this._currentOrganisationState.id}/${this._currentWorkspace.name}/runs/${this._currentRun.id}`
          });
        }
      }
    } else {
      this.items = [{
        title: 'Login',
        link: '/login'
      }]
    }   
  }

  toggleSidebar(): boolean {
    this.sidebarService.toggle();
    return false;
  }
}
