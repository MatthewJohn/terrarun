import { Component, OnInit } from '@angular/core';
import { FormBuilder } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { OrganisationService } from 'src/app/organisation.service';

@Component({
  selector: 'app-settings-general',
  templateUrl: './general.component.html',
  styleUrls: ['./general.component.scss']
})
export class GeneralComponent implements OnInit {

  nameValidStates = {
    invalid: {icon: 'close-outline', valid: false, iconStatus: 'danger'},
    valid: {icon: 'checkmark-circle-outline', valid: true, iconStatus: 'success'},
    loading: {icon: 'loader-outline', valid: false, iconStatus: 'info'},
    unchanged: {icon: '', valid: true, iconStatus: ''}
  };
  nameValid: {icon: string, valid: boolean, iconStatus: string} = this.nameValidStates.unchanged;
  form = this.formBuilder.group({
    name: '',
    email: ''
  });
  _organisationName: string | null = null;
  _originalOrgSettings: any = {};

  constructor(private formBuilder: FormBuilder,
              private organisationService: OrganisationService,
              private router: Router,
              private route: ActivatedRoute) {
    this.route.paramMap.subscribe((params) => {
      this._organisationName = params.get('organisationName');

      this.organisationService.getOrganisationDetails(this._organisationName || '').then((orgDetails) => {
        this._originalOrgSettings = orgDetails
        this.form.setValue({
          name: orgDetails.attributes.name,
          email: orgDetails.attributes.email
        })
      });
    });
  }

  ngOnInit(): void {
  }

  validateName(): void {
    this.nameValid = this.nameValidStates.loading;
    // Check if name is same as original value
    if (this.form.value.name == this._originalOrgSettings.attributes.name) {
      this.nameValid = this.nameValidStates.unchanged;
      return;
    }

    this.organisationService.validateNewOrganisationName(this.form.value.name).then((validationResult) => {
      this.nameValid = validationResult.valid ? this.nameValidStates.valid : this.nameValidStates.invalid;
    });
  }

  onSubmit(): void {
    this.organisationService.update(
      this._organisationName || '',
      this.form.value.name,
      this.form.value.email
    ).then((orgData) => {
      console.log(orgData);
      if (orgData.data.id != this._organisationName) {
        this.router.navigateByUrl(`/${orgData.data.id}/settings`)
      }
    });
  }
}
