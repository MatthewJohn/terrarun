import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { WorkspaceRoutingModule } from './workspace-routing.module';
import { RunModule } from '../run/run.module';
import { OverviewComponent } from './overview/overview.component';
import { RunListComponent } from './run-list/run-list.component';
import { NbButtonModule, NbCardModule, NbFormFieldModule, NbIconModule, NbInputModule, NbLayoutModule, NbSelectComponent, NbSelectModule, NbTagModule, NbToggleModule, NbTreeGridModule } from '@nebular/theme';
import { TaskListComponent } from './task-list/task-list.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { SettingsComponent } from './settings/settings.component';
import { ComponentsModule } from '../components/components.module';


@NgModule({
  declarations: [
    OverviewComponent,
    RunListComponent,
    TaskListComponent,
    SettingsComponent
  ],
  imports: [
    CommonModule,
    WorkspaceRoutingModule,
    RunModule,

    ComponentsModule,

    NbFormFieldModule,
    NbInputModule,
    NbToggleModule,
    NbButtonModule,
    NbSelectModule,

    NbLayoutModule,
    NbCardModule,
    NbTreeGridModule,
    NbIconModule,
    NbTagModule,

    FormsModule,
    ReactiveFormsModule,
  ]
})
export class WorkspaceModule { }
