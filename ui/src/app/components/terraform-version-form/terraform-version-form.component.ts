import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { FormBuilder } from '@angular/forms';
import { Observable, Subscription } from 'rxjs';
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

  private resetFormSubscription: Subscription | null = null;

  @Input()
  resetForm: Observable<void> | null = null;

  _initialData: ResponseObject<AdminTerraformVersion> | null = null;

  @Input()
  showLoading: boolean = false;

  @Input()
  get initialData(): ResponseObject<AdminTerraformVersion> | null {
    return this._initialData;
  }
  set initialData(value: ResponseObject<AdminTerraformVersion> | null) {
    this._initialData = value;
    this.resetFormData();
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
    if (this.resetForm !== null) {
      this.resetFormSubscription = this.resetForm.subscribe(() => {
        this.resetFormData();
      });
    }
  }

  ngOnDestroy() {
    if (this.resetFormSubscription !== null) {
      this.resetFormSubscription.unsubscribe();
    }
  }

  resetFormData() {
    if (this._initialData !== null) {
      this.formData.setValue({
        version: this._initialData.attributes.version,
        downloadUrl: this._initialData.attributes.url,
        checksumUrl: this._initialData.attributes['checksum-url'],
        checksumSha: this._initialData.attributes.sha,
        enabled: this._initialData.attributes.enabled,
        deprecated: this._initialData.attributes.deprecated,
        deprecatedReason: this._initialData.attributes['deprecated-reason']
      })

      // Disable version input
      this.formData.get('version')?.disable();

      // Disable deprecated message, if deprecated is unset
      this.onChangeDeprecation();
    } else {
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

      // Reset deprecation disable
      this.onChangeDeprecation();
    }
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
    // Emit create/update event
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
  }

  onFormCancel() {
    this.onCancel.emit(null);
  }

  onFormDelete() {
    if (this.initialData !== null) {
      // Emit delete event
      this.onDelete.emit(this.initialData.id);
    }
  }
}
