import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LifecycleExistsGuard } from 'src/app/guards/lifecycle-exists.guard';
import { EditComponent } from './edit/edit.component';
import { ListComponent } from './list/list.component';

const routes: Routes = [
  {
    path: '',
    component: ListComponent
  },
  {
    path: ':lifecycleName',
    component: EditComponent,
    canActivate: [LifecycleExistsGuard]
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class LifecycleRoutingModule { }
