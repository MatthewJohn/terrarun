import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { FormBuilder } from '@angular/forms';
import { NbDialogRef } from '@nebular/theme';
import { RunCreateAttributes } from 'src/app/interfaces/run-create-attributes';

@Component({
  selector: 'app-trigger-run-popup',
  templateUrl: './trigger-run-popup.component.html',
  styleUrls: ['./trigger-run-popup.component.scss']
})
export class TriggerRunPopupComponent implements OnInit {
  @Input()
  canDestroy: boolean = false;

  // Hold form information for run
  triggerForm = this.formBuilder.group({
    comment: '',
    type: 'apply',
    destroyConfirmation: ''
  });

  // Whether input for TerraformVersion should be shown
  showTerraformVersion: boolean = false;

  // Selected terraform version
  terraformVersion: string = "";

  // Whether to show destroy confirmation
  showTerraformDestroyConfirmation: boolean = false;

  // Show destroy configuration validation error
  showTerraformDestroyValidationError: boolean = false;

  constructor(
    protected ref: NbDialogRef<RunCreateAttributes|null>,
    private formBuilder: FormBuilder,
  ) {
  }

  ngOnInit(): void {
  }

  onTypeChange() {
    // Update whether Terraform Version field should be shown
    this.showTerraformVersion = this.triggerForm.get("type")?.value == "plan";

    // Update whether destroy confirmation is shown
    this.showTerraformDestroyConfirmation = this.triggerForm.get("type")?.value == "destroy";
  }

  onSubmit() {
    // Check if destroy confirmation checkbox is shown
    if (this.triggerForm.get("type")?.value == "destroy" && this.triggerForm.get("destroyConfirmation")?.value != "destroy") {
      this.showTerraformDestroyValidationError = true;
      return;
    }
    this.ref.close({
      "message": this.triggerForm.get("comment")?.value,
      "terraform-version": this.triggerForm.get("type")?.value == "plan" ? this.terraformVersion : null,
      "plan-only": this.triggerForm.get("type")?.value == "plan",
      "is-destroy": this.triggerForm.get("type")?.value == "destroy",
      "refresh": true,
      "refresh-only": this.triggerForm.get("type")?.value == "refresh",
    });
  }

  dismiss() {
    this.ref.close(null);
  }
}
