import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { RunRoutingModule } from './run-routing.module';
import { OverviewComponent } from './overview/overview.component';


@NgModule({
  declarations: [
    OverviewComponent
  ],
  imports: [
    CommonModule,
    RunRoutingModule
  ]
})
export class RunModule { }
