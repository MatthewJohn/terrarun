import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoggedInGuard } from '../logged-in.guard';
import { CreateComponent } from './create/create.component';
import { ListComponent } from './list/list.component';
import { OrganisationExistsGuard } from './organisation-exists.guard';
import { OverviewComponent } from './overview/overview.component';
import { SettingsComponent } from './settings/settings.component';
import { WorkspaceListComponent } from './workspace-list/workspace-list.component';

const routes: Routes = [
  {
    path: 'organisation/create',
    component: CreateComponent,
    canActivate: [LoggedInGuard]
  },
  {
    path: 'organisation/list',
    component: ListComponent,
    canActivate: [LoggedInGuard]
  },
  {
    path: ':organisationId',
    component: OverviewComponent,
    canActivate: [LoggedInGuard, OrganisationExistsGuard]
  },
  {
    path: ':organisationId/workspaces',
    component: WorkspaceListComponent,
    canActivate: [LoggedInGuard, OrganisationExistsGuard]
  },
  {
    path: ':organisationId/settings',
    component: SettingsComponent,
    canActivate: [LoggedInGuard, OrganisationExistsGuard]
  },
  {
    path: ':organisationId/:workspaceId',
    loadChildren: () => import(`../workspace/workspace.module`).then(m => m.WorkspaceModule),
    canActivate: [LoggedInGuard, OrganisationExistsGuard]
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class OrganisationRoutingModule { }
