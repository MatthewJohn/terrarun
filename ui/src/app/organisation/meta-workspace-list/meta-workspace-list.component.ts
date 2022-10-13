import { Component, OnInit } from '@angular/core';
import { FormBuilder } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { map, Observable, switchMap } from 'rxjs';
import { MetaWorkspaceService } from 'src/app/meta-workspace.service';
import { OrganisationService } from 'src/app/organisation.service';
import { OrganisationStateType, StateService } from 'src/app/state.service';
import { WorkspaceService } from 'src/app/workspace.service';

@Component({
  selector: 'app-meta-workspace-list',
  templateUrl: './meta-workspace-list.component.html',
  styleUrls: ['./meta-workspace-list.component.scss']
})
export class MetaWorkspaceListComponent implements OnInit {

  metaWorkspaces$: Observable<any>;
  tableColumns: string[] = ['name', 'description'];

  nameValidStates = {
    invalid: {icon: 'close-outline', valid: false, iconStatus: 'danger'},
    valid: {icon: 'checkmark-circle-outline', valid: true, iconStatus: 'success'},
    loading: {icon: 'loader-outline', valid: false, iconStatus: 'info'}
  };
  nameValid: {icon: string, valid: boolean, iconStatus: string} = this.nameValidStates.invalid;
  form = this.formBuilder.group({
    name: '',
    description: ''
  });

  currentOrganisation: OrganisationStateType | null = null;

  constructor(private state: StateService,
              private organisationService: OrganisationService,
              private metaWorkspaceService: MetaWorkspaceService,
              private router: Router,
              private route: ActivatedRoute,
              private formBuilder: FormBuilder) {
    this.metaWorkspaces$ = new Observable();
    this.state.currentOrganisation.subscribe((organisationData) => {
      if (organisationData.name) {
        this.currentOrganisation = organisationData;
        this.metaWorkspaces$ = this.organisationService.getAllMetaWorkspaces(organisationData.name).pipe(
          map((data) => {
            return Array.from({length: data.length},
              (_, n) => ({'data': data[n]})
            );
          })
        );
      }
    });
  }

  ngOnInit(): void {

  }

  validateName(): void {
    this.nameValid = this.nameValidStates.loading;

    this.metaWorkspaceService.validateNewName(this.currentOrganisation?.name || '', this.form.value.name).then((validationResult) => {
      this.nameValid = validationResult.valid ? this.nameValidStates.valid : this.nameValidStates.invalid;
    });
  }
  onCreate(): void {
    this.metaWorkspaceService.create(this.currentOrganisation?.name || '',
                                 this.form.value.name,
                                 this.form.value.description
                                 ).then((metaWorkspace) => {
      console.log(metaWorkspace);
      this.router.navigateByUrl(`/${this.currentOrganisation?.name}/projects/${metaWorkspace.data.attributes.name}`);
    });
  }

  onMetaWorkspaceClick(target: any) {
    console.log(target.data)
    this.router.navigateByUrl(`/${this.currentOrganisation?.name}/projects/${target.data.attributes.name}`)
  }
}
