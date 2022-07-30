import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { SettingsComponent } from './settings/settings.component';
import { TokensComponent } from './tokens/tokens.component';

const routes: Routes = [
  {
    path: '',
    children: [
      {
        path: '',
        component: SettingsComponent
      },
      {
        path: 'tokens',
        component: TokensComponent
      }
    ]
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class SettingsRoutingModule { }
