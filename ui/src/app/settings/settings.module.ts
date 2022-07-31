import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { SettingsRoutingModule } from './settings-routing.module';
import { TokensComponent } from './tokens/tokens.component';
import { SettingsComponent } from './settings/settings.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { NbButtonModule, NbCardModule, NbFormFieldModule, NbInputModule, NbTable, NbTableModule } from '@nebular/theme';


@NgModule({
  declarations: [
    TokensComponent,
    SettingsComponent
  ],
  imports: [
    CommonModule,
    SettingsRoutingModule,

    NbCardModule,
    NbFormFieldModule,
    NbButtonModule,
    NbInputModule,
    NbTableModule,

    FormsModule,
    ReactiveFormsModule
  ]
})
export class SettingsModule { }
