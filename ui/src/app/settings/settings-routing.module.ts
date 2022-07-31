import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoggedInGuard } from '../logged-in.guard';
import { SettingsComponent } from './settings/settings.component';
import { TokensComponent } from './tokens/tokens.component';

const routes: Routes = [
  {
    path: '',
    component: SettingsComponent,
    canActivate: [LoggedInGuard]
  },
  {
    path: 'tokens',
    component: TokensComponent,
    canActivate: [LoggedInGuard]
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class SettingsRoutingModule { }
