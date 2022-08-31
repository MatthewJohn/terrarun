import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { WorkspaceRoutingModule } from './workspace-routing.module';
import { RunModule } from '../run/run.module';
import { OverviewComponent } from './overview/overview.component';
import { RunListComponent } from './run-list/run-list.component';
import { NbCardModule, NbIconModule, NbLayoutModule, NbTagModule, NbTreeGridModule } from '@nebular/theme';
import { TaskListComponent } from './task-list/task-list.component';


@NgModule({
  declarations: [
    OverviewComponent,
    RunListComponent,
    TaskListComponent
  ],
  imports: [
    CommonModule,
    WorkspaceRoutingModule,
    RunModule,

    NbLayoutModule,
    NbCardModule,
    NbTreeGridModule,
    NbIconModule,
    NbTagModule
  ]
})
export class WorkspaceModule { }