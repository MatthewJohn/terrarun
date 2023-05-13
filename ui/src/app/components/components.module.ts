import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ErrorDialogueComponent } from './error-dialogue/error-dialogue.component';
import { NbButtonModule, NbCardModule, NbCheckboxModule, NbFormFieldModule, NbInputModule, NbListModule, NbRadioModule, NbSelectModule, NbSpinnerModule, NbTagModule } from '@nebular/theme';
import { VcsSelectionComponent } from './vcs-selection/vcs-selection.component';
import { TriggerRunPopupComponent } from './trigger-run-popup/trigger-run-popup.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { TerraformVersionFormComponent } from './terraform-version-form/terraform-version-form.component';



@NgModule({
  declarations: [
    ErrorDialogueComponent,
    VcsSelectionComponent,
    TriggerRunPopupComponent,
    TerraformVersionFormComponent
  ],
  imports: [
    CommonModule,

    NbCardModule,
    NbButtonModule,
    NbListModule,
    NbInputModule,
    NbSelectModule,
    NbFormFieldModule,
    NbRadioModule,
    NbTagModule,
    NbCheckboxModule,
    FormsModule,
    ReactiveFormsModule,
    NbSpinnerModule,
  ],
  bootstrap: [
    ErrorDialogueComponent,
    VcsSelectionComponent,
    TriggerRunPopupComponent,
    TerraformVersionFormComponent,
  ],
  exports: [
    VcsSelectionComponent,
    TriggerRunPopupComponent,
    TerraformVersionFormComponent,
  ]
})
export class ComponentsModule { }
