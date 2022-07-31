import { Component } from '@angular/core';
import { NbMenuItem, NbSidebarService } from '@nebular/theme';
import { HomeComponent } from './home/home.component';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'ui';

  constructor(private readonly sidebarService: NbSidebarService) {
  }

  toggleSidebar(): boolean {
    this.sidebarService.toggle();
    return false;
  }
  items: NbMenuItem[] = [
    {
      title: 'Home',
      link: '/home',
      icon: 'home-outline'
    },
    {
      title: 'Create',
      icon: 'plus-square-outline',
      children: [
        {
          title: 'Organisation',
          link: '/organisation/create'
        }
      ]
    },
    {
      title: 'Workspaces',
      link: '/workspaces',
      children: [
        {
          title: 'Create',
          link: '/workspaces/create'
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
}
