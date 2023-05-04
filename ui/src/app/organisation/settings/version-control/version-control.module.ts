import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { VersionControlRoutingModule } from './version-control-routing.module';
import { OverviewComponent } from './overview/overview.component';
import { NewComponent } from './new/new.component';


@NgModule({
  declarations: [
    OverviewComponent,
    NewComponent
  ],
  imports: [
    CommonModule,
    VersionControlRoutingModule
  ]
})
export class VersionControlModule { }
