import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ErrorDialogueComponent } from './error-dialogue/error-dialogue.component';
import { NbButtonModule, NbCardModule, NbCheckboxModule, NbFormFieldModule, NbInputModule, NbListModule, NbRadioModule, NbSelectModule, NbSpinnerModule, NbTagModule, NbToggleModule } from '@nebular/theme';
import { VcsSelectionComponent } from './vcs-selection/vcs-selection.component';
import { TriggerRunPopupComponent } from './trigger-run-popup/trigger-run-popup.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { TerraformVersionFormComponent } from './terraform-version-form/terraform-version-form.component';
import { TerraformVersionSelectComponent } from './terraform-version-select/terraform-version-select.component';
import { ProjectWorkspaceSettingsComponent } from './project-workspace-settings/project-workspace-settings.component';



@NgModule({
  declarations: [
    ErrorDialogueComponent,
    VcsSelectionComponent,
    TriggerRunPopupComponent,
    TerraformVersionFormComponent,
    TerraformVersionSelectComponent,
    ProjectWorkspaceSettingsComponent,
  ],
  imports: [
    CommonModule,

    NbCardModule,
    NbButtonModule,
    NbListModule,
    NbInputModule,
    NbSelectModule,
    NbToggleModule,
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
    TerraformVersionSelectComponent,
    ProjectWorkspaceSettingsComponent,
  ],
  exports: [
    VcsSelectionComponent,
    TriggerRunPopupComponent,
    TerraformVersionFormComponent,
    TerraformVersionSelectComponent,
    ProjectWorkspaceSettingsComponent,
  ]
})
export class ComponentsModule { }
