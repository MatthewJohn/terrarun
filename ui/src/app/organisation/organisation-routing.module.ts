import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoggedInGuard } from '../logged-in.guard';
import { CreateComponent } from './create/create.component';

const routes: Routes = [
  {
    path: 'organisation/create',
    component: CreateComponent,
    canActivate: [LoggedInGuard]
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class OrganisationRoutingModule { }
