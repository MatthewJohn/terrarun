import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { VersionControlRoutingModule } from './version-control-routing.module';
import { OverviewComponent } from './overview/overview.component';
import { NewComponent } from './new/new.component';
import { NbButtonModule, NbCardModule, NbFormFieldModule, NbInputModule, NbSelectModule, NbStepperModule } from '@nebular/theme';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';


@NgModule({
  declarations: [
    OverviewComponent,
    NewComponent
  ],
  imports: [
    CommonModule,
    VersionControlRoutingModule,

    NbCardModule,
    NbInputModule,
    NbButtonModule,
    NbStepperModule,

    FormsModule,
    ReactiveFormsModule,
    NbFormFieldModule,
    NbSelectModule
  ]
})
export class VersionControlModule { }
