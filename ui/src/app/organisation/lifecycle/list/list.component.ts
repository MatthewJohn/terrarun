import { Component, OnInit } from '@angular/core';
import { FormBuilder } from '@angular/forms';
import { Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { DataItem, DataList } from 'src/app/interfaces/data';
import { LifecycleAttributes } from 'src/app/interfaces/lifecycle-attributes';
import { ResponseObject } from 'src/app/interfaces/response';
import { LifecycleService } from 'src/app/services/lifecycle.service';
import { OrganisationStateType, StateService } from 'src/app/state.service';

@Component({
  selector: 'app-list',
  templateUrl: './list.component.html',
  styleUrls: ['./list.component.scss']
})
export class ListComponent implements OnInit {

  tableColumns: string[] = ['name', 'description'];

  // List of environment lifecycles in organisation
  lifecycles: ResponseObject<LifecycleAttributes>[] = [];
  // Formatted environment lifecycles for dataList
  lifecyclesRowData: DataItem<ResponseObject<LifecycleAttributes>>[] = [];

  // Whether list of environment lifecycles is loading
  listSpinner: boolean = false;
  createSpinner: boolean = false;

  // Pre-defined states for name validation
  nameValidStates = {
    invalid: {icon: 'close-outline', valid: false, iconStatus: 'danger'},
    valid: {icon: 'checkmark-circle-outline', valid: true, iconStatus: 'success'},
    loading: {icon: 'loader-outline', valid: false, iconStatus: 'info'}
  };

  // Validation state of new environment lifecycle
  createNameValid: {icon: string, valid: boolean, iconStatus: string} = this.nameValidStates.invalid;

  // Form for new environment lifecycle 
  createForm = this.formBuilder.group({
    name: '',
    description: ''
  });

  // Current organisation and subscription to StateService
  currentOrganisation: OrganisationStateType | null = null;
  currentOrganisationSubscription: Subscription | null = null;

  constructor(
    private formBuilder: FormBuilder,
    private stateService: StateService,
    private lifecycleService: LifecycleService,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.currentOrganisationSubscription = this.stateService.currentOrganisation.subscribe((currentOrganisation) => {
      this.currentOrganisation = currentOrganisation;
      this.getLifecycleList();
    });
  }

  ngOnDestroy() {
    if (this.currentOrganisationSubscription) {
      this.currentOrganisationSubscription.unsubscribe();
    }
  }

  onCreate() {
    if (this.currentOrganisation?.name) {
      this.createSpinner = true;
      this.lifecycleService.create(
        this.currentOrganisation?.name,
        {
          name: this.createForm.value.name,
          description: this.createForm.value.description,
          "allow-per-workspace-vcs": false
        }
      ).then(() => {
        // Refresh environment list
        this.getLifecycleList();

        // Reset create form
        this.createForm.setValue({
          name: '',
          description: ''
        });
        this.createSpinner = false;
      });
    }
  }

  validateNewName() {
    this.createNameValid = this.nameValidStates.loading;

    if (this.currentOrganisation?.name) {
      this.lifecycleService.validateNewName(
        this.currentOrganisation.name,
        this.createForm.value.name
      ).then((validationResult) => {
        this.createNameValid = validationResult.data.valid ? this.nameValidStates.valid : this.nameValidStates.invalid;
      });
    }
  }

  onLifecycleClick(row: DataItem<ResponseObject<LifecycleAttributes>>) {
    this.router.navigateByUrl(`/${this.currentOrganisation?.name}/lifecycles/${row.data.attributes.name}`);
  }


  getLifecycleList(): void {
    if (this.currentOrganisation?.name) {
      this.listSpinner = true;
      this.lifecycleService.getLifecycles(
        this.currentOrganisation.name
      ).then((lifecycles: ResponseObject<LifecycleAttributes>[]) => {
        this.lifecycles = lifecycles;
        this.lifecyclesRowData = this.lifecycles.map((val) => {return {data: val}});
        this.listSpinner = false;
      });
    }
  }

}
