import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { SiteAdminRoutingModule } from './site-admin-routing.module';
import { TerraformVersionsComponent } from './terraform-versions/terraform-versions.component';
import { NbCardModule, NbLayoutModule, NbTableModule, NbTreeGridModule } from '@nebular/theme';


@NgModule({
  declarations: [
    TerraformVersionsComponent
  ],
  imports: [
    CommonModule,
    SiteAdminRoutingModule,

    NbLayoutModule,
    NbTableModule,
    NbCardModule,
    NbTreeGridModule,
  ]
})
export class SiteAdminModule { }
