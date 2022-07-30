import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomeComponent } from './home/home.component';

const routes: Routes = [
  {
    path: 'home',
    component: HomeComponent
  },
  {
    path: 'settings',
    loadChildren: () => import(`./settings/settings.module`).then(m => m.SettingsModule)
  },

  // Redirect app/* URLs to root
  // {
  //   path: 'app',
  //   redirectTo: '/',
  //   pathMatch: 'prefix'
  // },
  {path: '', redirectTo: 'home', pathMatch: 'full'}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
