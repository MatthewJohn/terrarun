import { Component, OnInit } from '@angular/core';
import { FormBuilder } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { map, Observable, switchMap } from 'rxjs';
import { OrganisationService } from 'src/app/organisation.service';
import { OrganisationStateType, StateService } from 'src/app/state.service';
import { WorkspaceService } from 'src/app/workspace.service';

@Component({
  selector: 'app-workspace-list',
  templateUrl: './workspace-list.component.html',
  styleUrls: ['./workspace-list.component.scss']
})
export class WorkspaceListComponent implements OnInit {

  workspaces$: Observable<any>;
  tableColumns: string[] = ['name'];
  organisationName: string | null = null;

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
              private workspaceService: WorkspaceService,
              private router: Router,
              private route: ActivatedRoute,
              private formBuilder: FormBuilder) {
    this.workspaces$ = this.route.paramMap.pipe(
      switchMap(params => {
        this.organisationName = params.get('organisationName');
        return this.organisationService.getAllWorkspaces(this.organisationName || "").pipe(
          map((data) => {
            return Array.from({length: data.length},
              (_, n) => ({'data': data[n]}))
          })
        );
      })
    );

    this.state.currentOrganisation.subscribe((data) => this.currentOrganisation = data);
  }

  ngOnInit(): void {

  }

  validateName(): void {
    this.nameValid = this.nameValidStates.loading;

    this.workspaceService.validateNewWorkspaceName(this.organisationName || '', this.form.value.name).then((validationResult) => {
      this.nameValid = validationResult.valid ? this.nameValidStates.valid : this.nameValidStates.invalid;
    });
  }
  onCreate(): void {
    this.workspaceService.create(this.organisationName || '',
                                 this.form.value.name,
                                 this.form.value.description
                                 ).then((workspace) => {
      console.log(workspace);
      this.router.navigateByUrl(`/${this.organisationName}/${workspace.data.attributes.name}`);
    });
  }

  onWorkspaceClick(target: any) {
    console.log(target.data)
    this.router.navigateByUrl(`/${this.organisationName}/${target.data.attributes.name}`)
  }
}
