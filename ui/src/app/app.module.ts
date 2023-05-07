import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { NbActionsModule, NbButtonModule, NbCardModule, NbDialogModule, NbFormFieldModule, NbIconConfig, NbIconModule, NbInputModule, NbLayoutModule, NbMenuModule, NbSidebarModule, NbThemeModule } from '@nebular/theme';
import { NbEvaIconsModule } from '@nebular/eva-icons';
import { HomeComponent } from './home/home.component';
import { SettingsModule } from './settings/settings.module';
import { HttpClientModule } from '@angular/common/http';
import { LoginComponent } from './login/login.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { AppRedirectComponent } from './app-redirect/app-redirect.component';
import { OrganisationModule } from './organisation/organisation.module';

@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    LoginComponent,
    AppRedirectComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    SettingsModule,
    BrowserAnimationsModule,
  
    NbIconModule,
    NbSidebarModule.forRoot(),
    NbMenuModule.forRoot(),
    NbThemeModule.forRoot({ name: 'default' }),
    NbDialogModule.forRoot(),
    NbLayoutModule,
    NbEvaIconsModule,
    NbInputModule,
    NbCardModule,
    NbButtonModule,
    NbFormFieldModule,
    NbActionsModule,
    NbEvaIconsModule,

    HttpClientModule,
    FormsModule,
    ReactiveFormsModule,
    OrganisationModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})


export class AppModule {
  disabledIconConfig: NbIconConfig = { icon: 'settings-2-outline', pack: 'eva' };
}
