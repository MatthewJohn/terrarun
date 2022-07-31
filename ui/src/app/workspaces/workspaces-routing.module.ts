import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { CreateComponent } from './create/create.component';
import { WorkspacesComponent } from './workspaces.component';

const routes: Routes = [
  { path: '', component: WorkspacesComponent },
  { path: 'create', component: CreateComponent }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class WorkspacesRoutingModule { }
