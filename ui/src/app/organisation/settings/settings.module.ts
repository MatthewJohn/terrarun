import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { SettingsRoutingModule } from './settings-routing.module';
import { GeneralComponent } from './general/general.component';
import { NbButtonModule, NbCardModule, NbFormFieldModule, NbIconModule, NbInputModule, NbLayoutModule } from '@nebular/theme';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';


@NgModule({
  declarations: [
    GeneralComponent
  ],
  imports: [
    CommonModule,

    NbCardModule,
    NbLayoutModule,

    // NbToggleModule,
    // NbTreeGridModule,
    // NbSelectModule,
    FormsModule,
    ReactiveFormsModule,
    NbFormFieldModule,
    NbIconModule,

    NbInputModule,
    NbButtonModule,

    SettingsRoutingModule
  ]
})
export class SettingsModule { }
