import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { GeneralComponent } from './general/general.component';

const routes: Routes = [
  {
    path: '',
    component: GeneralComponent
  },
  {
    path: 'general',
    component: GeneralComponent
  },
  {
    path: 'version-control',
    loadChildren: () => import(`./version-control/version-control.module`).then(m => m.VersionControlModule)
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class SettingsRoutingModule { }
