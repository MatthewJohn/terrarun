import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { AccountRoutingModule } from './account-routing.module';
import { TokensComponent } from './tokens/tokens.component';
import { AccountComponent } from './account/account.component';


@NgModule({
  declarations: [
    TokensComponent,
    AccountComponent
  ],
  imports: [
    CommonModule,
    AccountRoutingModule
  ]
})
export class AccountModule { }
