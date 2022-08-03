import { Component } from '@angular/core';
import { NbMenuItem, NbSidebarService } from '@nebular/theme';
import { AccountService } from './account.service';
import { HomeComponent } from './home/home.component';
import { StateService } from './state.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'ui';

  constructor(private readonly sidebarService: NbSidebarService,
              private accountService: AccountService,
              private stateService: StateService) {
    this.accountService.getAccountDetails();

    this.stateService.authenticationState.subscribe((data) => {
      if (data.authenticated) {
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
      } else {
        this.items = [{
          title: 'Login',
          link: '/login'
        }]
      }
    });
  }

  toggleSidebar(): boolean {
    this.sidebarService.toggle();
    return false;
  }
  items: NbMenuItem[] = [];
}
