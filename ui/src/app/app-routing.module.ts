import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AppRedirectComponent } from './app-redirect/app-redirect.component';
import { HomeComponent } from './home/home.component';
import { LoggedInGuard } from './logged-in.guard';
import { LoginComponent } from './login/login.component';

const routes: Routes = [
  {
    path: 'home',
    component: HomeComponent,
    canActivate: [LoggedInGuard]
  },
  {
    path: 'settings',
    loadChildren: () => import(`./settings/settings.module`).then(m => m.SettingsModule),
    canActivate: [LoggedInGuard]
  },
  {
    path: 'login',
    component: LoginComponent
  },

  // Redirect app/* URLs to root
  {
    path: 'app',
    children: [
      {
        path: '**',
        component: AppRedirectComponent
      }
    ]
  },
  {
    // Redirect empty URL to home
    path: '', redirectTo: 'home', pathMatch: 'full'
  },
  {
    path: 'workspaces',
    loadChildren: () => import('./workspaces/workspaces.module').then(m => m.WorkspacesModule),
    canActivate: [LoggedInGuard]
  },
  {
    path: '*',
    loadChildren: () => import(`./organisation/organisation.module`).then(m => m.OrganisationModule),
    canActivate: [LoggedInGuard]
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
