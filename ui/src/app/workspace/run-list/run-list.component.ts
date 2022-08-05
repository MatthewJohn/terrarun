import { Component, OnInit } from '@angular/core';
import { FormBuilder } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { map, Observable, switchMap } from 'rxjs';
import { OrganisationService } from 'src/app/organisation.service';
import { OrganisationStateType, StateService, WorkspaceStateType } from 'src/app/state.service';
import { WorkspaceService } from 'src/app/workspace.service';

@Component({
  selector: 'app-run-list',
  templateUrl: './run-list.component.html',
  styleUrls: ['./run-list.component.scss']
})
export class RunListComponent implements OnInit {

  runs$: Observable<any> | null = null;
  tableColumns: string[] = ['name'];
  workspaceName: string | null = null;
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
  currentWorkspace: WorkspaceStateType | null = null;

  constructor(private state: StateService,
              private workspaceService: WorkspaceService,
              private router: Router,
              private route: ActivatedRoute,
              private formBuilder: FormBuilder) {
    this.state.currentWorkspace.subscribe((data) => {
      this.currentWorkspace = data;
      if (data.id) {
        this.runs$ = this.workspaceService.getRuns(data.id).pipe(
          map((data) => {
            return Array.from({length: data.data.length},
              (_, n) => ({'data': data.data[n]}))
          })
        );
      }
    });

    this.state.currentOrganisation.subscribe((data) => this.currentOrganisation = data);
  }

  ngOnInit(): void {
  }


  onWorkspaceClick(target: any) {
    this.router.navigateByUrl(`/${this.currentOrganisation?.id}/${target.data.name}`)
  }

}
