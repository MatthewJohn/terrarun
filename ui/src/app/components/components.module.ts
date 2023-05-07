import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ErrorDialogueComponent } from './error-dialogue/error-dialogue.component';
import { NbButtonModule, NbCardModule, NbListModule } from '@nebular/theme';
import { VcsSelectionComponent } from './vcs-selection/vcs-selection.component';



@NgModule({
  declarations: [
    ErrorDialogueComponent,
    VcsSelectionComponent
  ],
  imports: [
    CommonModule,

    NbCardModule,
    NbButtonModule,
    NbListModule,
  ],
  bootstrap: [
    ErrorDialogueComponent,
    VcsSelectionComponent
  ],
  exports: [
    VcsSelectionComponent
  ]
})
export class ComponentsModule { }
