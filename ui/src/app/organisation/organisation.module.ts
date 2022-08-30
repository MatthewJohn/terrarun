import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { OrganisationRoutingModule } from './organisation-routing.module';
import { CreateComponent } from './create/create.component';
import { NbButtonModule, NbCardModule, NbCheckboxModule, NbFormFieldModule, NbIconModule, NbInputModule, NbLayoutModule, NbTreeGridModule } from '@nebular/theme';
import { FormBuilder, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { ListComponent } from './list/list.component';
import { WorkspaceListComponent } from './workspace-list/workspace-list.component';
import { OverviewComponent } from './overview/overview.component';
import { SettingsComponent } from './settings/settings.component';
import { WorkspaceModule } from '../workspace/workspace.module';
import { TaskListComponent } from './task-list/task-list.component';


@NgModule({
  declarations: [
    CreateComponent,
    ListComponent,
    WorkspaceListComponent,
    TaskListComponent,
    OverviewComponent,
    SettingsComponent
  ],
  imports: [
    CommonModule,
    OrganisationRoutingModule,

    NbCardModule,
    NbFormFieldModule,
    NbLayoutModule,
    NbInputModule,
    NbCheckboxModule,
    NbIconModule,
    NbButtonModule,
    NbTreeGridModule,

    FormsModule,
    ReactiveFormsModule,
    WorkspaceModule,
  ]
})
export class OrganisationModule { }
