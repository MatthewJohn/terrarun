import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AccountComponent } from './account/account.component';
import { TokensComponent } from './tokens/tokens.component';

const routes: Routes = [
  {
    path: 'account',
    component: AccountComponent
  },
  {
    path: 'tokens',
    component: TokensComponent
  },
  {path: '', redirectTo: 'account', pathMatch: 'full'},
  {path: '**', redirectTo: 'account'},
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class AccountRoutingModule { }
