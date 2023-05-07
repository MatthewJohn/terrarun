import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { OrganisationRoutingModule } from './organisation-routing.module';
import { CreateComponent } from './create/create.component';
import { NbButtonModule, NbCardModule, NbCheckboxModule, NbFormFieldModule, NbIconModule, NbInputModule, NbLayoutModule, NbSelectModule, NbToggleModule, NbTreeGridModule } from '@nebular/theme';
import { FormBuilder, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { ListComponent } from './list/list.component';
import { WorkspaceListComponent } from './workspace-list/workspace-list.component';
import { OverviewComponent } from './overview/overview.component';
import { WorkspaceModule } from '../workspace/workspace.module';
import { TaskListComponent } from './task-list/task-list.component';
import { ProjectListComponent } from './project-list/project-list.component';


@NgModule({
  declarations: [
    CreateComponent,
    ListComponent,
    WorkspaceListComponent,
    TaskListComponent,
    ProjectListComponent,
    OverviewComponent,
  ],
  imports: [
    CommonModule,
    OrganisationRoutingModule,

    NbCardModule,
    NbFormFieldModule,
    NbLayoutModule,
    NbInputModule,
    NbToggleModule,
    NbIconModule,
    NbButtonModule,
    NbTreeGridModule,
    NbSelectModule,

    FormsModule,
    ReactiveFormsModule,
    WorkspaceModule,
  ]
})
export class OrganisationModule { }
