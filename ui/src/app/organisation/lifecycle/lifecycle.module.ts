import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { LifecycleRoutingModule } from './lifecycle-routing.module';
import { ListComponent } from './list/list.component';
import { NbAccordionModule, NbButtonModule, NbCardModule, NbFormFieldModule, NbIconModule, NbInputModule, NbLayoutModule, NbSelectModule, NbSpinnerModule, NbToggleModule, NbTreeGridModule } from '@nebular/theme';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { EditComponent } from './edit/edit.component';


@NgModule({
  declarations: [
    ListComponent,
    EditComponent
  ],
  imports: [
    CommonModule,
    LifecycleRoutingModule,

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
    NbSelectModule,
    NbAccordionModule,
    NbToggleModule,
  ]
})
export class LifecycleModule { }
