import { Component, Input, OnInit } from '@angular/core';
import { ControlContainer, Form, FormControlName, FormGroup, FormGroupDirective } from '@angular/forms';
import { ResponseObject } from 'src/app/interfaces/response';
import { TerraformVersion } from 'src/app/interfaces/terraform-version';
import { TerraformVersionService } from 'src/app/services/terraform-version.service';

@Component({
  selector: 'terraform-version-select',
  templateUrl: './terraform-version-select.component.html',
  styleUrls: ['./terraform-version-select.component.scss'],
  viewProviders: [
    {
        provide: ControlContainer,
        useExisting: FormGroupDirective
    }
  ]
})
export class TerraformVersionSelectComponent implements OnInit {

  @Input()
  formControlName: string | undefined;

  @Input()
  formGroup: FormGroup | undefined;

  loadingData: boolean = true;
  terraformVersions: ResponseObject<TerraformVersion>[] = [];

  constructor(
    private terraformVersionService: TerraformVersionService
  ) { }

  getFormGroup(): FormGroup {
    if (this.formGroup) {
      return this.formGroup
    }
    throw new Error();
  }
  getFormControlName(): string {
    if (this.formControlName) {
      return this.formControlName;
    }
    throw new Error();
  }

  ngOnInit(): void {
    this.terraformVersionService.getVersions().then((terraformVersions) => {
      this.terraformVersions = terraformVersions;
    });
  }

}
