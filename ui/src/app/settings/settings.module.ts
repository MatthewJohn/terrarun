import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { SettingsRoutingModule } from './settings-routing.module';
import { TokensComponent } from './tokens/tokens.component';
import { SettingsComponent } from './settings/settings.component';


@NgModule({
  declarations: [
    TokensComponent,
    SettingsComponent
  ],
  imports: [
    CommonModule,
    SettingsRoutingModule
  ]
})
export class SettingsModule { }
