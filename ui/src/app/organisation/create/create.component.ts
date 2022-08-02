import { Component, OnInit } from '@angular/core';
import { FormBuilder } from '@angular/forms';
import { Router } from '@angular/router';
import { OrganisationService } from 'src/app/organisation.service';

@Component({
  selector: 'app-create',
  templateUrl: './create.component.html',
  styleUrls: ['./create.component.scss']
})
export class CreateComponent implements OnInit {


  nameValidStates = {
    invalid: {icon: 'close-outline', valid: false, iconStatus: 'danger'},
    valid: {icon: 'checkmark-circle-outline', valid: true, iconStatus: 'success'},
    loading: {icon: 'loader-outline', valid: false, iconStatus: 'info'}
  };
  nameValid: {icon: string, valid: boolean, iconStatus: string} = this.nameValidStates.invalid;
  form = this.formBuilder.group({
    name: '',
    email: ''
  });
  organisationSlug: string = '';

  constructor(private formBuilder: FormBuilder,
              private organisationService: OrganisationService,
              private router: Router) { }

  validateName(): void {
    this.nameValid = this.nameValidStates.loading;
    this.organisationService.validateNewOrganisationName(this.form.value.name).then((validationResult) => {
      this.nameValid = validationResult.valid ? this.nameValidStates.valid : this.nameValidStates.invalid;
      this.organisationSlug = validationResult.valid ? validationResult.name_id : '';
    });
  }

  onCreate(): void {
    this.organisationService.create(this.form.value.name, this.form.value.email).then((orgData) => {
      console.log(orgData);
    });
  }

  ngOnInit(): void {
  }

}
