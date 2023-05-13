import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { ControlContainer, Form, FormBuilder, FormControlName, FormGroup, FormGroupDirective } from '@angular/forms';
import { ResponseObject } from 'src/app/interfaces/response';
import { TerraformVersion } from 'src/app/interfaces/terraform-version';
import { TerraformVersionService } from 'src/app/services/terraform-version.service';

@Component({
  selector: 'terraform-version-select',
  templateUrl: './terraform-version-select.component.html',
  styleUrls: ['./terraform-version-select.component.scss']
})
export class TerraformVersionSelectComponent implements OnInit {

  @Input()
  value: string = "";

  @Output()
  valueChange = new EventEmitter<string>();

  loadingData: boolean = true;
  terraformVersions: ResponseObject<TerraformVersion>[] = [];

  constructor(
    private terraformVersionService: TerraformVersionService
  ) {
  }

  ngOnInit(): void {
    this.terraformVersionService.getVersions().then((terraformVersions) => {
      this.terraformVersions = terraformVersions;
      this.loadingData = false;
    });
  }

  // onSelect() {
  //   console.log("got new version");
  //   this.value = this.formGroup.value.terraformVersion;
  //   this.valueChange.emit(this.value);
  // }

}
