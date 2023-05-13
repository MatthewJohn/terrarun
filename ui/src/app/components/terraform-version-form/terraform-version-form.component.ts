import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { FormBuilder } from '@angular/forms';
import { AdminTerraformVersion } from 'src/app/interfaces/admin-terraform-version';
import { ResponseObject } from 'src/app/interfaces/response';

@Component({
  selector: 'app-terraform-version-form',
  templateUrl: './terraform-version-form.component.html',
  styleUrls: ['./terraform-version-form.component.scss']
})
export class TerraformVersionFormComponent implements OnInit {

  @Input()
  show: boolean = true;

  @Input()
  showCancel: boolean = false;

  @Input()
  showDelete: boolean = false;

  @Input()
  title: string = "";

  @Input()
  submitMessage: string = "";

  @Output()
  onSubmit: EventEmitter<AdminTerraformVersion> = new EventEmitter();

  @Output()
  onCancel: EventEmitter<null> = new EventEmitter();

  @Output()
  onDelete: EventEmitter<string> = new EventEmitter();

  _initialData: ResponseObject<AdminTerraformVersion> | null = null;

  @Input()
  get initialData(): ResponseObject<AdminTerraformVersion> | null {
    return this._initialData;
  }
  set initialData(value: ResponseObject<AdminTerraformVersion> | null) {
    this._initialData = value;
    if (value !== null) {
      this.formData.setValue({
        version: value.attributes.version,
        downloadUrl: value.attributes.url,
        checksumUrl: value.attributes['checksum-url'],
        checksumSha: value.attributes.sha,
        enabled: value.attributes.enabled,
        deprecated: value.attributes.deprecated,
        deprecatedReason: value.attributes['deprecated-reason']
      })

      // Disable version input
      this.formData.get('version')?.disable();

      // Disable deprecated message, if deprecated is unset
      this.onChangeDeprecation();
    }
  }

  formData = this.formBuilder.group({
    version: '',
    downloadUrl: '',
    checksumUrl: '',
    checksumSha: '',
    enabled: true,
    deprecated: false,
    deprecatedReason: ''
  });

  constructor(
    private formBuilder: FormBuilder
  ) {
    this.formData.get('deprecatedReason')?.disable();
  }

  ngOnInit(): void {
  }

  onChangeDeprecation() {
    if (this.formData.value.deprecated) {
      this.formData.get('deprecatedReason')?.enable();
    } else {
      this.formData.get('deprecatedReason')?.setValue('');
      this.formData.get('deprecatedReason')?.disable();
    }
  }

  onFormSubmit() {
    this.onSubmit.emit({
      version: this.formData.value.version,
      url: this.formData.value.downloadUrl,
      "checksum-url": this.formData.value.checksumUrl,
      sha: this.formData.value.checksumSha,
      deprecated: this.formData.value.deprecated,
      "deprecated-reason": this.formData.value.deprecatedReason,
      enabled: this.formData.value.enabled,

      beta: undefined,
      official: undefined,
      "created-at": undefined,
      usage: undefined
    });
    // Reset form data
    this.formData.setValue({
      version: '',
      downloadUrl: '',
      checksumUrl: '',
      checksumSha: '',
      enabled: true,
      deprecated: false,
      deprecatedReason: ''
    });
  }

  onFormCancel() {
    this.onCancel.emit(null);
  }

  onFormDelete() {
    if (this.initialData !== null) {
      this.onDelete.emit(this.initialData.id);
    }
  }

}
