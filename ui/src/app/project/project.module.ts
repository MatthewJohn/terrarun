import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NbButtonModule, NbFormFieldModule, NbLayoutModule, NbListModule, NbSelectModule } from '@nebular/theme';


import { ProjectRoutingModule } from './project-routing.module';
import { OverviewComponent } from './overview/overview.component';
import { NbCardModule } from '@nebular/theme';
import { ComponentsModule } from '../components/components.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';


@NgModule({
  declarations: [
    OverviewComponent
  ],
  imports: [
    NbCardModule,
    NbButtonModule,
    NbListModule,

    ComponentsModule,
    NbSelectModule,

    NbFormFieldModule,
    FormsModule,
    ReactiveFormsModule,
    NbLayoutModule,

    CommonModule,
    ProjectRoutingModule
  ]
})
export class ProjectModule { }
