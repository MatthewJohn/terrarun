import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ErrorDialogueComponent } from './error-dialogue/error-dialogue.component';
import { NbButtonModule, NbCardModule } from '@nebular/theme';



@NgModule({
  declarations: [
    ErrorDialogueComponent
  ],
  imports: [
    CommonModule,

    NbCardModule,
    NbButtonModule,
  ],
  bootstrap: [
    ErrorDialogueComponent
  ]
})
export class ComponentsModule { }
