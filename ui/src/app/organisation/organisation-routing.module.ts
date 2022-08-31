import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoggedInGuard } from '../logged-in.guard';
import { WorkspaceExistsGuard } from '../workspace-exists.guard';
import { CreateComponent } from './create/create.component';
import { ListComponent } from './list/list.component';
import { OrganisationExistsGuard } from './organisation-exists.guard';
import { OverviewComponent } from './overview/overview.component';
import { SettingsComponent } from './settings/settings.component';
import { TaskListComponent } from './task-list/task-list.component';
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
    path: ':organisationName',
    component: OverviewComponent,
    canActivate: [LoggedInGuard, OrganisationExistsGuard]
  },
  {
    path: ':organisationName/workspaces',
    component: WorkspaceListComponent,
    canActivate: [LoggedInGuard, OrganisationExistsGuard]
  },
  {
    path: ':organisationName/tasks',
    component: TaskListComponent,
    canActivate: [LoggedInGuard, OrganisationExistsGuard]
  },
  {
    path: ':organisationName/settings',
    component: SettingsComponent,
    canActivate: [LoggedInGuard, OrganisationExistsGuard]
  },
  {
    path: ':organisationName/:workspaceName',
    loadChildren: () => import(`../workspace/workspace.module`).then(m => m.WorkspaceModule),
    canActivate: [LoggedInGuard, OrganisationExistsGuard, WorkspaceExistsGuard]
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class OrganisationRoutingModule { }