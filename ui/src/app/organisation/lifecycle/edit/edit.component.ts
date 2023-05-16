import { Component, OnInit } from '@angular/core';
import { Subscription } from 'rxjs';
import { EnvironmentService } from 'src/app/environment.service';
import { LifecycleAttributes } from 'src/app/interfaces/lifecycle-attributes';
import { LifecycleEnvironmentAttributes, LifecycleEnvironmentRelationships } from 'src/app/interfaces/lifecycle-environment-attributes';
import { LifecycleEnvironmentGroupAttributes, LifecycleEnvironmentGroupRelationships } from 'src/app/interfaces/lifecycle-environment-group-attributes';
import { LifecycleEnvironmentGroupService } from 'src/app/services/lifecycle-environment-group.service';
import { LifecycleEnvironmentService } from 'src/app/services/lifecycle-environment.service';
import { LifecycleService } from 'src/app/services/lifecycle.service';
import { LifecycleStateType, OrganisationStateType, StateService } from 'src/app/state.service';

import { EnvironmentAttributes } from '../../../interfaces/environment';
import { ResponseObject, ResponseObjectWithRelationships } from '../../../interfaces/response';

// Create custom LifecycleEnvironmentGroupAttributes that converts
// null minimum constraints to empty string, to support
// empty field in nb-select
type LifecycleEnvironmentGroupAttributesForm = Omit<LifecycleEnvironmentGroupAttributes, 'minimum-runs' | 'minimum-successful-plans' | 'minimum-successful-applies'> & {
  'minimum-runs': '' | number;
  'minimum-successful-plans': '' | number;
  'minimum-successful-applies': '' | number;
}

interface RowDataType {
  // Data attribute is LifecycleGroupdata with additional environmentItx list attribute
  data: ResponseObjectWithRelationships<LifecycleEnvironmentGroupAttributesForm, LifecycleEnvironmentGroupRelationships> & {
    environmentItx: number[];
  }
  children: {
    data: ResponseObject<LifecycleEnvironmentAttributes>
  }[];
  expanded: boolean;
}

@Component({
  selector: 'app-edit',
  templateUrl: './edit.component.html',
  styleUrls: ['./edit.component.scss']
})
export class EditComponent implements OnInit {

  availableEnvironments: ResponseObject<EnvironmentAttributes>[] = [];
  lifecycleData: ResponseObject<LifecycleAttributes> | null = null;

  stateServiceLifecycleSubscription: Subscription | null = null;
  stateServiceOrganisationSubscription: Subscription | null = null;
  currentLifecycle: LifecycleStateType | null = null;
  currentOrganisation: OrganisationStateType | null = null;

  lifecycleEnvironmentGroups: ResponseObjectWithRelationships<LifecycleEnvironmentGroupAttributes, LifecycleEnvironmentGroupRelationships>[] = [];

  rowData: RowDataType[] = [];

  // List of lifecycle environments keyed by lifecycle environment group
  lifecycleEnvironments: {[key: string]: ResponseObjectWithRelationships<LifecycleEnvironmentAttributes, LifecycleEnvironmentRelationships>[]} = {};

  // List of lifecycle environment group to environment ID mappings for stored value for environment addition form
  newEnvironmentData: {[key: string]: string} = {};

  nameColumn: string[] = ['name'];
  actionColumn: string[] = ['actions'];
  allColumns: string[] = [...this.nameColumn, ...this.actionColumn];

  constructor(
    private stateService: StateService,
    private lifecycleService: LifecycleService,
    private environmentService: EnvironmentService,
    private lifecycleEnvironmentGroupService: LifecycleEnvironmentGroupService,
    private lifecycleEnvironmentService: LifecycleEnvironmentService
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
    // Do not call until both organisation and lifecycle have been populated
    if (this.currentOrganisation?.name && this.currentLifecycle?.name) {

      // Obtain list of environments
      this.environmentService.getOrganisationEnvironments(
        this.currentOrganisation.name
      ).then((environments) => {
        this.availableEnvironments = environments;

        if (this.currentOrganisation?.name && this.currentLifecycle?.name) {
          // Get lifecycle details
          this.lifecycleService.getByName(
            this.currentOrganisation.name,
            this.currentLifecycle.name
          ).then((lifecycleData) => {
            this.lifecycleData = lifecycleData;

            // Reset row data and new environment data to handle reloads
            this.rowData = [];
            this.newEnvironmentData = {};

            // Get all lifecycle environment groups
            this.lifecycleService.getLifecycleEnvironmentGroups(this.lifecycleData.id).then((lifecycleEnvironmentGroups) => {
              this.lifecycleEnvironmentGroups = lifecycleEnvironmentGroups;

              // Get all lifecycle environments for the group
              this.lifecycleEnvironmentGroups.forEach((lifecycleEnvironmentGroup) => {

                // Add to list of new environments
                this.newEnvironmentData[lifecycleEnvironmentGroup.id] = "";

                // Add lifecycle group to list of table data
                this.rowData = [{
                  data: {
                    // Create array of environment itx (1.. number of environments) to display
                    // in drop-down for environment rules
                    environmentItx: Array.from(lifecycleEnvironmentGroup.relationships['lifecycle-environments'].data.keys()).map((val) => val + 1),
                    ...lifecycleEnvironmentGroup,
                    attributes: {
                      ...lifecycleEnvironmentGroup.attributes,
                      // Replace minimum-X attributes with empty string, if they are none
                      "minimum-runs": (
                        lifecycleEnvironmentGroup.attributes['minimum-runs'] != null ?
                        lifecycleEnvironmentGroup.attributes['minimum-runs'] : ''
                      ),
                      "minimum-successful-plans": (
                        lifecycleEnvironmentGroup.attributes['minimum-successful-plans'] != null ?
                        lifecycleEnvironmentGroup.attributes['minimum-successful-plans'] : ''
                      ),
                      "minimum-successful-applies": (
                        lifecycleEnvironmentGroup.attributes['minimum-successful-applies'] != null ?
                        lifecycleEnvironmentGroup.attributes['minimum-successful-applies'] : ''
                      ),
                    }
                  },
                  children: [],
                  expanded: true
                }, ...this.rowData];

                // Order existing rows
                this.rowData = this.rowData.sort((a, b) => {return a.data.attributes.order - b.data.attributes.order;});

                this.lifecycleEnvironmentGroupService.getLifecycleEnvironments(lifecycleEnvironmentGroup.id).then((lifecycleEnvironments) => {
                  this.lifecycleEnvironments[lifecycleEnvironmentGroup.id] = lifecycleEnvironments;

                  // Iterate through each lifecycle environment and
                  // add to children in row data and
                  // remove the associated environment from list of available environments
                  lifecycleEnvironments.forEach((lifecycleEnvironment) => {
                    // Create child item in row data
                    this.rowData.filter((row) => {return row.data.id == lifecycleEnvironmentGroup.id})[0]?.children.push({
                      data: lifecycleEnvironment
                    });
                    this.rowData = [...this.rowData];

                    this.availableEnvironments = this.availableEnvironments.filter((environment) => {return environment.id !== lifecycleEnvironment.relationships.environment.data.id})
                  });

                });
              });
            });
          });
        }

      });
    }
  }

  onCreateLifecycleEnvironmentGroup() {
    console.log("Creating lifecycle environment");
    if (this.currentLifecycle?.id) {
      this.lifecycleService.createLifecycleEnvironmentGroup(this.currentLifecycle.id).then(() => {
        this.getLifecycleData();
      })
    }
  }

  onLifecycleEnvironmentGroupSettingsSave(lifecycleEnvironmentGroup: ResponseObjectWithRelationships<LifecycleEnvironmentGroupAttributesForm, LifecycleEnvironmentGroupRelationships>) {
    console.log("Saving");
    console.log(lifecycleEnvironmentGroup);
    this.lifecycleEnvironmentGroupService.update(
      lifecycleEnvironmentGroup.id,
      {
        ...lifecycleEnvironmentGroup.attributes,
        "minimum-runs": (
          lifecycleEnvironmentGroup.attributes['minimum-runs'] != '' ?
          // Parse through "Number" as the nb-select is treating 0 as a string
          Number(lifecycleEnvironmentGroup.attributes['minimum-runs']) : null
        ),
        "minimum-successful-plans": (
          lifecycleEnvironmentGroup.attributes['minimum-successful-plans'] != '' ?
          // Parse through "Number" as the nb-select is treating 0 as a string
          Number(lifecycleEnvironmentGroup.attributes['minimum-successful-plans']) : null
        ),
        "minimum-successful-applies": (
          lifecycleEnvironmentGroup.attributes['minimum-successful-applies'] != '' ?
          // Parse through "Number" as the nb-select is treating 0 as a string
          Number(lifecycleEnvironmentGroup.attributes['minimum-successful-applies']) : null
        )
      }
    ).then(() => {
      this.getLifecycleData();
    })
  }

  onLifecycleEnvironmentGroupDelete(lifecycleEnvironmentGroupId: string) {
    console.log('deleting ' + lifecycleEnvironmentGroupId)
    this.lifecycleEnvironmentGroupService.delete(lifecycleEnvironmentGroupId).then(() => {
      this.getLifecycleData();
    })
  }

  onLifecycleEnvironmentCreate(lifecycleEnvironmentGroupId: string) {
    console.log('creating environment in ' + lifecycleEnvironmentGroupId)
    this.lifecycleEnvironmentGroupService.createLifecycleEnvironment(
      lifecycleEnvironmentGroupId,
      this.newEnvironmentData[lifecycleEnvironmentGroupId]
    ).then(() => {
      this.getLifecycleData();
    })
  }

  onLifecycleEnvironmentDelete(lifecycleEnvironmentId: string) {
    this.lifecycleEnvironmentService.delete(lifecycleEnvironmentId).then(() => {
      this.getLifecycleData();
    })
  }

}
