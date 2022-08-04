import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoggedInGuard } from '../logged-in.guard';
import { RunExistsGuard } from '../run-exists.guard';
import { WorkspaceExistsGuard } from '../workspace-exists.guard';
import { OverviewComponent } from './overview/overview.component';

const routes: Routes = [
  {
    path: '',
    component: OverviewComponent,
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
