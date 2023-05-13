import { Component, forwardRef, Input, OnInit } from '@angular/core';
import { ControlContainer, ControlValueAccessor, Form, FormControlName, FormGroup, FormGroupDirective, NG_VALUE_ACCESSOR } from '@angular/forms';
import { ResponseObject } from 'src/app/interfaces/response';
import { TerraformVersion } from 'src/app/interfaces/terraform-version';
import { TerraformVersionService } from 'src/app/services/terraform-version.service';

@Component({
  selector: 'terraform-version-select',
  templateUrl: './terraform-version-select.component.html',
  styleUrls: ['./terraform-version-select.component.scss'],
  providers: [{ 
    provide: NG_VALUE_ACCESSOR,
    multi: true,
    useExisting: forwardRef(() => TerraformVersionSelectComponent),
  }],
})
export class TerraformVersionSelectComponent implements ControlValueAccessor {

  loadingData: boolean = true;
  terraformVersions: ResponseObject<TerraformVersion>[] = [];

  constructor(
    private terraformVersionService: TerraformVersionService
  ) { }

  value: string = "";
  onChange() {}
  onTouched() {}
  isDisabled: boolean = false;

  writeValue(value: string) {
    this.value = value
  }

  registerOnChange(fn: any) {
    this.onChange = fn
  }

  registerOnTouched(fn: any) {
    this.onTouched = fn
  }

  setDisabledState(isDisabled: boolean) {
    this.isDisabled = isDisabled;
  }

  ngOnInit(): void {
    this.terraformVersionService.getVersions().then((terraformVersions) => {
      this.terraformVersions = terraformVersions;
    });
  }

}
