import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { WorkspaceRoutingModule } from './workspace-routing.module';
import { RunModule } from '../run/run.module';
import { OverviewComponent } from './overview/overview.component';
import { RunListComponent } from './run-list/run-list.component';
import { NbCardModule, NbIconModule, NbLayoutModule, NbTreeGridModule } from '@nebular/theme';


@NgModule({
  declarations: [
    OverviewComponent,
    RunListComponent
  ],
  imports: [
    CommonModule,
    WorkspaceRoutingModule,
    RunModule,

    NbLayoutModule,
    NbCardModule,
    NbTreeGridModule,
    NbIconModule
  ]
})
export class WorkspaceModule { }
