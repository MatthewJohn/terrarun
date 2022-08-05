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
  tableColumns: string[] = ['id', 'status', 'created-at'];
  workspaceName: string | null = null;
  organisationName: string | null = null;


  currentOrganisation: OrganisationStateType | null = null;
  currentWorkspace: WorkspaceStateType | null = null;

  constructor(private state: StateService,
              private workspaceService: WorkspaceService,
              private router: Router,
              private route: ActivatedRoute,
              private formBuilder: FormBuilder) {
    this.state.currentWorkspace.subscribe((data) => {
      this.currentWorkspace = data;
      setInterval(() => {
        this.runs$ = this.workspaceService.getRuns(data.id || '').pipe(
          map((data) => {
            return Array.from({length: data.data.length},
              (_, n) => ({'data': {id: data.data[n].id, ...data.data[n].attributes}}))
          })
        );
      }, 1000);
    });

    this.state.currentOrganisation.subscribe((data) => this.currentOrganisation = data);
  }

  ngOnInit(): void {
  }


  onWorkspaceClick(target: any) {
    this.router.navigateByUrl(`/${this.currentOrganisation?.id}/${target.data.name}`)
  }

}
