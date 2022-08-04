import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { WorkspaceRoutingModule } from './workspace-routing.module';
import { RunModule } from '../run/run.module';


@NgModule({
  declarations: [],
  imports: [
    CommonModule,
    WorkspaceRoutingModule,
    RunModule
  ]
})
export class WorkspaceModule { }
