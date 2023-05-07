import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ErrorDialogueComponent } from './error-dialogue/error-dialogue.component';
import { NbButtonModule, NbCardModule, NbFormFieldModule, NbInputModule, NbListModule, NbSelectModule } from '@nebular/theme';
import { VcsSelectionComponent } from './vcs-selection/vcs-selection.component';
import { TriggerRunPopupComponent } from './trigger-run-popup/trigger-run-popup.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';



@NgModule({
  declarations: [
    ErrorDialogueComponent,
    VcsSelectionComponent,
    TriggerRunPopupComponent
  ],
  imports: [
    CommonModule,

    NbCardModule,
    NbButtonModule,
    NbListModule,
    NbInputModule,
    NbSelectModule,
    NbFormFieldModule,
    FormsModule,
    ReactiveFormsModule,
  ],
  bootstrap: [
    ErrorDialogueComponent,
    VcsSelectionComponent,
    TriggerRunPopupComponent,
  ],
  exports: [
    VcsSelectionComponent,
    TriggerRunPopupComponent,
  ]
})
export class ComponentsModule { }
