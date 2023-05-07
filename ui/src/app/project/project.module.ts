import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NbButtonModule, NbListModule } from '@nebular/theme';


import { ProjectRoutingModule } from './project-routing.module';
import { OverviewComponent } from './overview/overview.component';
import { NbCardModule } from '@nebular/theme';
import { ComponentsModule } from '../components/components.module';


@NgModule({
  declarations: [
    OverviewComponent
  ],
  imports: [
    NbCardModule,
    NbButtonModule,
    NbListModule,

    ComponentsModule,

    CommonModule,
    ProjectRoutingModule
  ]
})
export class ProjectModule { }
