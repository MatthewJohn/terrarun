import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { SettingsRoutingModule } from './settings-routing.module';
import { GeneralComponent } from './general/general.component';
import { NbButtonModule, NbCardModule, NbFormFieldModule, NbIconModule, NbInputModule, NbLayoutModule } from '@nebular/theme';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { ComponentsModule } from 'src/app/components/components.module';


@NgModule({
  declarations: [
    GeneralComponent
  ],
  imports: [
    CommonModule,

    NbCardModule,
    NbLayoutModule,

    ComponentsModule,

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
