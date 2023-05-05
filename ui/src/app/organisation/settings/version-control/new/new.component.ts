import { Component, OnInit } from '@angular/core';
import { AbstractControl, FormBuilder, FormControl, FormGroup, ValidationErrors, Validators } from '@angular/forms';
import { NbStepChangeEvent } from '@nebular/theme';

interface ValidatorFn {
  (control: AbstractControl): ValidationErrors | null
}

@Component({
  selector: 'app-new',
  templateUrl: './new.component.html',
  styleUrls: ['./new.component.scss']
})
export class NewComponent implements OnInit {

  basicDetailsForm: FormGroup;
  secretsForm: FormGroup;

  changeEvent: NbStepChangeEvent|null;

  oauthClientDetails: any;

  constructor(
    private formBuilder: FormBuilder,
  ) {
    this.changeEvent = null;
    this.basicDetailsForm = this.formBuilder.group({
      name: '',
      serviceProvider: '',
      httpUrl: '',
      apiUrl: ''
    });
    this.basicDetailsForm.setValidators(this.getBasicDetailsFormValidators());

    this.secretsForm = this.formBuilder.group({
      clientId: '',
      clientSecret: ''
    });
    this.oauthClientDetails = null;
  }

  ngOnInit(): void {
  }

  onServiceProviderChange() {
    // Update default HTTP URL and API after change of service provider
    if (this.basicDetailsForm.get('serviceProvider')?.value == 'github') {
      let formValues = this.basicDetailsForm.value;
      formValues.httpUrl = 'https://github.com';
      formValues.apiUrl = 'https://api.github.com'
      this.basicDetailsForm.setValue(formValues);
    }
  }

  handleStepChange(e: NbStepChangeEvent): void {
    this.changeEvent = e;
    // If going forwards in steps
    if (this.changeEvent.index > this.changeEvent.previouslySelectedIndex) {
      // Check the step progress
      if (this.changeEvent.index == 1) {
        // Move to step 2
        this.onSetBasicDetails();
      }
    }
  }

  getBasicDetailsFormValidators() : ValidatorFn {
    let myFun = (c: AbstractControl): ValidationErrors | null => {
      console.log(c.get('name'));
      if (c.valid) return null;
      else return {something: 'someError'};
    };
    return myFun;
   }

  onSetBasicDetails() {
    console.log("Called onSetBasicDetails")
  }

}
