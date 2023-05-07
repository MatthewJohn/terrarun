import { Component, Input, OnInit } from '@angular/core';
import { NbDialogRef } from '@nebular/theme';

@Component({
  selector: 'app-error-dialogue',
  templateUrl: './error-dialogue.component.html',
  styleUrls: ['./error-dialogue.component.scss']
})
export class ErrorDialogueComponent {
  @Input()
  data: string = '';

  constructor(protected ref: NbDialogRef<ErrorDialogueComponent>) {
  }

  dismiss() {
    this.ref.close();
  }

}
