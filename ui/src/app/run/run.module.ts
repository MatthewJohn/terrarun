import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { RunRoutingModule } from './run-routing.module';
import { OverviewComponent } from './overview/overview.component';
import { NbAccordionModule, NbAlertModule, NbCardModule } from '@nebular/theme';


@NgModule({
  declarations: [
    OverviewComponent
  ],
  imports: [
    CommonModule,
    RunRoutingModule,

    NbAccordionModule,
    NbCardModule,
    NbAlertModule
  ]
})
export class RunModule { }
