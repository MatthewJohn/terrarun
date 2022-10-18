import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { ProjectRoutingModule } from './project-routing.module';
import { OverviewComponent } from './overview/overview.component';
import { NbCardModule } from '@nebular/theme';


@NgModule({
  declarations: [
    OverviewComponent
  ],
  imports: [
    NbCardModule,

    CommonModule,
    ProjectRoutingModule
  ]
})
export class ProjectModule { }
