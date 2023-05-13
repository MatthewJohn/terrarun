import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { EnvironmentLifecycleRoutingModule } from './environment-lifecycle-routing.module';
import { ListComponent } from './list/list.component';
import { NbButtonModule, NbCardModule, NbFormFieldModule, NbIconModule, NbInputModule, NbLayoutModule, NbSpinnerModule, NbTreeGridModule } from '@nebular/theme';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';


@NgModule({
  declarations: [
    ListComponent
  ],
  imports: [
    CommonModule,
    EnvironmentLifecycleRoutingModule,

    NbLayoutModule,
    NbCardModule,
    NbFormFieldModule,
    ReactiveFormsModule,
    FormsModule,
    NbTreeGridModule,
    NbIconModule,
    NbInputModule,
    NbButtonModule,
    NbSpinnerModule,
  ]
})
export class EnvironmentLifecycleModule { }
