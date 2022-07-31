import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { WorkspacesRoutingModule } from './workspaces-routing.module';
import { WorkspacesComponent } from './workspaces.component';
import { CreateComponent } from './create/create.component';
import { NbButtonModule, NbCardModule, NbFormFieldModule, NbInputModule, NbTableModule } from '@nebular/theme';
import { FormBuilder, FormsModule, ReactiveFormsModule } from '@angular/forms';


@NgModule({
  declarations: [
    WorkspacesComponent,
    CreateComponent
  ],
  imports: [
    CommonModule,
    WorkspacesRoutingModule,

    NbCardModule,
    NbFormFieldModule,
    NbButtonModule,
    NbInputModule,
    NbCardModule,

    FormsModule,
    ReactiveFormsModule
  ]
})
export class WorkspacesModule { }
