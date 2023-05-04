import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NbButtonModule } from '@nebular/theme';


import { ProjectRoutingModule } from './project-routing.module';
import { OverviewComponent } from './overview/overview.component';
import { NbCardModule } from '@nebular/theme';


@NgModule({
  declarations: [
    OverviewComponent
  ],
  imports: [
    NbCardModule,
    NbButtonModule,

    CommonModule,
    ProjectRoutingModule
  ]
})
export class ProjectModule { }
