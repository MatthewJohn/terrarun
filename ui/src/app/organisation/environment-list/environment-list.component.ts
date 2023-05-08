import { Component, OnInit } from '@angular/core';
import { FormBuilder } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { map, Observable } from 'rxjs';
import { EnvironmentService } from 'src/app/environment.service';
import { OrganisationStateType, StateService } from 'src/app/state.service';

@Component({
  selector: 'app-environment-list',
  templateUrl: './environment-list.component.html',
  styleUrls: ['./environment-list.component.scss']
})
export class EnvironmentListComponent implements OnInit {
  environments$: Observable<any>;
  tableColumns: string[] = ['name', 'description'];
  organisationName: string | null = null;

  editEnvironment: any = null;

  nameValidStates = {
    invalid: {icon: 'close-outline', valid: false, iconStatus: 'danger'},
    valid: {icon: 'checkmark-circle-outline', valid: true, iconStatus: 'success'},
    loading: {icon: 'loader-outline', valid: false, iconStatus: 'info'}
  };

  createEnvironmentNameValid: {icon: string, valid: boolean, iconStatus: string} = this.nameValidStates.invalid;
  createForm = this.formBuilder.group({
    name: '',
    description: ''
  });

  editEnvironmentNameValid: {icon: string, valid: boolean, iconStatus: string} = this.nameValidStates.invalid;
  editForm = this.formBuilder.group({
    name: '',
    description: ''
  });

  currentOrganisation: OrganisationStateType | null = null;

  constructor(private state: StateService,
              private enviornmentService: EnvironmentService,
              private router: Router,
              private route: ActivatedRoute,
              private formBuilder: FormBuilder) {
    this.environments$ = new Observable();
    this.route.paramMap.subscribe(params => {
        this.organisationName = params.get('organisationName');
        this.getEnvironmentList();
    });

    this.state.currentOrganisation.subscribe((data) => this.currentOrganisation = data);
  }

  getEnvironmentList(): void {
    if (this.organisationName) {
      this.environments$ = this.enviornmentService.getOrganisationEnvironments(this.organisationName).pipe(
        map((data) => {
          return Array.from({length: data.data.length},
            (_, n) => ({'data': data.data[n]}))
        })
      );
    }
  }

  ngOnInit(): void {

  }

  validateNewEnvironmentName(): void {
    this.createEnvironmentNameValid = this.nameValidStates.loading;

    if (this.organisationName) {
      this.enviornmentService.validateNewName(
        this.organisationName,
        this.createForm.value.name
      ).then((validationResult) => {
        this.createEnvironmentNameValid = validationResult.data.valid ? this.nameValidStates.valid : this.nameValidStates.invalid;
      });
    }
  }
  onCreate(): void {
    if (this.organisationName) {
      this.enviornmentService.create(
        this.organisationName,
        this.createForm.value.name,
        this.createForm.value.description,
        
      ).then(() => {
        // Refresh environment list
        this.getEnvironmentList();

        // Reset create form
        this.editForm.setValue({
          name: '',
          description: ''
        })
      });
    }
  }

  validateEditEnvironmentName(): void {

    this.editEnvironmentNameValid = this.nameValidStates.loading;

    // If name matches original value, set as valid
    if (this.editForm.value.name == this.editEnvironment.attributes.name) {
      this.editEnvironmentNameValid = this.nameValidStates.valid;
      return;
    }

    if (this.organisationName) {
      this.enviornmentService.validateNewName(
        this.organisationName,
        this.editForm.value.name
      ).then((validationResult) => {
        this.editEnvironmentNameValid = validationResult.data.valid ? this.nameValidStates.valid : this.nameValidStates.invalid;
      });
    }
  }

  onEnvironmentClick(target: any) {
    // Setup edit form for environment
    this.editEnvironment = target.data;
    this.editForm.setValue({
      name: this.editEnvironment.attributes.name,
      description: this.editEnvironment.attributes.description
    });
    this.editEnvironmentNameValid = this.nameValidStates.valid;
  }
  cancelEdit() {
    this.editEnvironment = null;
  }
  onEdit() {
    this.enviornmentService.updateAttributes(
      this.editEnvironment.id,
      {name: this.editForm.value.name, description: this.editForm.value.description}
    ).then(() => {
      this.editEnvironment = null;
      this.getEnvironmentList();
    });
  }
}
