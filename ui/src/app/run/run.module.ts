import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { RunRoutingModule } from './run-routing.module';
import { OverviewComponent } from './overview/overview.component';
import { NbAccordionModule, NbAlertModule, NbButtonModule, NbCardModule, NbLayoutModule } from '@nebular/theme';
import { ComponentsModule } from '../components/components.module';


@NgModule({
  declarations: [
    OverviewComponent
  ],
  imports: [
    CommonModule,
    RunRoutingModule,

    NbAccordionModule,
    NbCardModule,
    NbAlertModule,
    NbButtonModule,
    NbLayoutModule,

    ComponentsModule,
  ]
})
export class RunModule { }
