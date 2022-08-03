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
  organisationId: string | null = null;

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
        this.organisationId = params.get('organisationId');
        return this.organisationService.getAllWorkspaces(this.organisationId || "").pipe(
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

    this.workspaceService.validateNewWorkspaceName(this.currentOrganisation?.name || '', this.form.value.name).then((validationResult) => {
      this.nameValid = validationResult.valid ? this.nameValidStates.valid : this.nameValidStates.invalid;
    });
  }
  onCreate(): void {

  }

  onWorkspaceClick(target: any) {
    this.router.navigateByUrl(`/${this.organisationId}/${target.data.name}`)
  }
}
