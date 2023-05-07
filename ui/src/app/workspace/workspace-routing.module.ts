import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoggedInGuard } from '../logged-in.guard';
import { RunExistsGuard } from '../run-exists.guard';
import { WorkspaceExistsGuard } from '../workspace-exists.guard';
import { OverviewComponent } from './overview/overview.component';
import { RunListComponent } from './run-list/run-list.component';
import { SettingsComponent } from './settings/settings.component';
import { TaskListComponent } from './task-list/task-list.component';

const routes: Routes = [
  {
    path: '',
    component: OverviewComponent,
  },
  {
    path: 'runs',
    component: RunListComponent,
  },
  {
    path: 'tasks',
    component: TaskListComponent
  },
  {
    path: 'settings',
    component: SettingsComponent
  },
  {
    path: 'runs/:runId',
    loadChildren: () => import(`../run/run.module`).then(m => m.RunModule),
    canActivate: [LoggedInGuard, WorkspaceExistsGuard, RunExistsGuard]
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class WorkspaceRoutingModule { }
