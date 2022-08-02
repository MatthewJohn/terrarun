import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { OrganisationRoutingModule } from './organisation-routing.module';
import { CreateComponent } from './create/create.component';
import { NbButtonModule, NbCardModule, NbFormFieldModule, NbIconModule, NbInputModule, NbLayoutModule } from '@nebular/theme';
import { FormBuilder, FormsModule, ReactiveFormsModule } from '@angular/forms';


@NgModule({
  declarations: [
    CreateComponent
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

    FormsModule,
    ReactiveFormsModule,
  ]
})
export class OrganisationModule { }
