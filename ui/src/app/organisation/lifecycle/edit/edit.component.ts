import { Component, OnInit } from '@angular/core';
import { Subscription } from 'rxjs';
import { LifecycleAttributes } from 'src/app/interfaces/lifecycle-attributes';
import { LifecycleService } from 'src/app/services/lifecycle.service';
import { LifecycleStateType, OrganisationStateType, StateService } from 'src/app/state.service';

import { Environment } from '../../../interfaces/environment';
import { ResponseObject } from '../../../interfaces/response';


@Component({
  selector: 'app-edit',
  templateUrl: './edit.component.html',
  styleUrls: ['./edit.component.scss']
})
export class EditComponent implements OnInit {

  availableEnvironments: ResponseObject<Environment>[] = [];
  lifecycleData: ResponseObject<LifecycleAttributes> | null = null;

  stateServiceLifecycleSubscription: Subscription | null = null;
  stateServiceOrganisationSubscription: Subscription | null = null;
  currentLifecycle: LifecycleStateType | null = null;
  currentOrganisation: OrganisationStateType | null = null;

  nameColumn: string[] = ['name'];
  actionColumn: string[] = ['actions'];
  allColumns: string[] = [...this.nameColumn, ...this.actionColumn];
  dataSource: any = [
    {
      data: {
        id: "blah", type: "lifecycle-environment-groups", attributes: {order: 1},
        // Custom value
        childItx: [1, 2]
      },
      expanded: true,
      children: [
        {data: {name: 'dev', type: "lifecycle-environments"}},
        {data: {name: 'test', type: "lifecycle-environments"}}
      ]
    },
    {
      data: {
        id: "blah2", attributes: {order: 2},
        // Custom value
        childItx: [1]
      },
      expanded: true,
      children: [
        {data: {name: 'prod', type: "lifecycle-environments"}},
      ]
    }
  ]

  constructor(
    private stateService: StateService,
    private lifecycleService: LifecycleService
  ) { }

  ngOnInit(): void {
    this.stateServiceOrganisationSubscription = this.stateService.currentOrganisation.subscribe((currentOrganisation) => {
      this.currentOrganisation = currentOrganisation;

      this.getLifecycleData();
    });

    this.stateServiceLifecycleSubscription = this.stateService.currentLifecycle.subscribe((currentLifecycle) => {
      this.currentLifecycle = currentLifecycle;

      this.getLifecycleData();
    })
  }

  ngOnDestroy(): void {
    if (this.stateServiceLifecycleSubscription) {
      this.stateServiceLifecycleSubscription.unsubscribe();
    }
    if (this.stateServiceOrganisationSubscription) {
      this.stateServiceOrganisationSubscription.unsubscribe();
    }
  }

  getLifecycleData() {
    if (this.currentOrganisation?.name && this.currentLifecycle?.name) {
      this.lifecycleService.getByName(
        this.currentOrganisation.name,
        this.currentLifecycle.name
      ).then((lifecycleData) => {
        this.lifecycleData = lifecycleData;
      })
    }
  }

}
