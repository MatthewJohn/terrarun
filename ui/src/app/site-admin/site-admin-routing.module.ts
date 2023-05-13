import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { TerraformVersionsComponent } from './terraform-versions/terraform-versions.component';

const routes: Routes = [
  {
    path: 'terraform-versions',
    component: TerraformVersionsComponent,
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class SiteAdminRoutingModule { }
