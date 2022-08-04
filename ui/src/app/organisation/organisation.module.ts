import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { OrganisationRoutingModule } from './organisation-routing.module';
import { CreateComponent } from './create/create.component';
import { NbButtonModule, NbCardModule, NbFormFieldModule, NbIconModule, NbInputModule, NbLayoutModule, NbTreeGridModule } from '@nebular/theme';
import { FormBuilder, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { ListComponent } from './list/list.component';
import { WorkspaceListComponent } from './workspace-list/workspace-list.component';
import { OverviewComponent } from './overview/overview.component';
import { SettingsComponent } from './settings/settings.component';


@NgModule({
  declarations: [
    CreateComponent,
    ListComponent,
    WorkspaceListComponent,
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
    NbIconModule,
    NbButtonModule,
    NbTreeGridModule,

    FormsModule,
    ReactiveFormsModule,
  ]
})
export class OrganisationModule { }
