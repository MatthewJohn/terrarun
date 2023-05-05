import { Component, OnInit } from '@angular/core';
import { AbstractControl, FormBuilder, FormControl, FormGroup, ValidationErrors, Validators } from '@angular/forms';
import { NbDialogService, NbStepChangeEvent } from '@nebular/theme';
import { ErrorDialogueComponent } from 'src/app/components/error-dialogue/error-dialogue.component';
import { OauthClientService } from 'src/app/services/oauth-client.service';
import { OrganisationStateType, StateService } from 'src/app/state.service';

interface ValidatorFn {
  (control: AbstractControl): ValidationErrors | null
}

@Component({
  selector: 'app-new',
  templateUrl: './new.component.html',
  styleUrls: ['./new.component.scss']
})
export class NewComponent implements OnInit {

  // Data for input forms for each step
  basicDetailsForm: FormGroup;
  secretsForm: FormGroup;

  // Change event when switching steps
  changeEvent: NbStepChangeEvent|null;

  // Store data for created oauth Client
  oauthClientData: any;

  // Store state about selected organisation
  currentOrganisation: OrganisationStateType | null = null;

  constructor(
    private stateService: StateService,
    private formBuilder: FormBuilder,
    private oauthClientService: OauthClientService,
    private dialogService: NbDialogService
  ) {
    // Subscribe to current organisation to obtain the current organisation
    this.stateService.currentOrganisation.subscribe((organisationData) => {
      this.currentOrganisation = organisationData;
    });

    // Set default data for form inputs and other member variables
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
    this.oauthClientData = null;
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

  showError(error: string) {
    this.dialogService.open(ErrorDialogueComponent, {
      context: {data: error}
    });
  }

  onSetBasicDetails() {
    console.log("Called onSetBasicDetails");
    if (this.currentOrganisation?.name) {
      this.oauthClientService.create(
        this.currentOrganisation.name,
        this.basicDetailsForm.get('name')?.value,
        this.basicDetailsForm.get('serviceProvider')?.value,
        this.basicDetailsForm.get('httpUrl')?.value,
        this.basicDetailsForm.get('apiUrl')?.value
      ).then((oauthClientData) => {
        console.log('Created oauth client');
        console.log(oauthClientData);
        this.oauthClientData = oauthClientData;
      }).catch(() => {
        this.showError("Failed to register application. Please reload the page and try again.")
      });
    }
  }
}
