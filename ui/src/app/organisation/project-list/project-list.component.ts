import { Component, OnInit } from '@angular/core';
import { FormBuilder } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { map, Observable, switchMap } from 'rxjs';
import { EnvironmentService } from 'src/app/environment.service';
import { LifecycleService } from 'src/app/lifecycle.service';
import { ProjectService } from 'src/app/project.service';
import { OrganisationService } from 'src/app/organisation.service';
import { OrganisationStateType, StateService } from 'src/app/state.service';
import { WorkspaceService } from 'src/app/workspace.service';

@Component({
  selector: 'app-project-list',
  templateUrl: './project-list.component.html',
  styleUrls: ['./project-list.component.scss']
})
export class ProjectListComponent implements OnInit {

  projects$: Observable<any>;
  organisationLifecycles$: Observable<any>;
  tableColumns: string[] = ['name', 'description'];

  nameValidStates = {
    invalid: {icon: 'close-outline', valid: false, iconStatus: 'danger'},
    valid: {icon: 'checkmark-circle-outline', valid: true, iconStatus: 'success'},
    loading: {icon: 'loader-outline', valid: false, iconStatus: 'info'}
  };
  nameValid: {icon: string, valid: boolean, iconStatus: string} = this.nameValidStates.invalid;
  form = this.formBuilder.group({
    name: '',
    description: '',
    lifecycle: null
  });

  currentOrganisation: OrganisationStateType | null = null;

  constructor(private state: StateService,
              private organisationService: OrganisationService,
              private projectService: ProjectService,
              private lifecycleService: LifecycleService,
              private router: Router,
              private route: ActivatedRoute,
              private formBuilder: FormBuilder) {
    this.projects$ = new Observable();
    this.organisationLifecycles$ = new Observable();

    this.state.currentOrganisation.subscribe((organisationData) => {
      if (organisationData.name) {
        this.organisationLifecycles$ = this.lifecycleService.getOrganisationLifecycles(organisationData.name);

        this.currentOrganisation = organisationData;

        this.projects$ = this.organisationService.getAllProjects(organisationData.name).pipe(
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

    this.projectService.validateNewName(this.currentOrganisation?.name || '', this.form.value.name).then((validationResult) => {
      this.nameValid = validationResult.valid ? this.nameValidStates.valid : this.nameValidStates.invalid;
    });
  }
  onCreate(): void {
    this.projectService.create(
      this.currentOrganisation?.name || '',
      this.form.value.name,
      this.form.value.description,
      this.form.value.lifecycle
    ).then((project) => {
      console.log(project);
      this.router.navigateByUrl(`/${this.currentOrganisation?.name}/projects/${project.data.attributes.name}`);
    });
  }

  onProjectClick(target: any) {
    console.log(target.data)
    this.router.navigateByUrl(`/${this.currentOrganisation?.name}/projects/${target.data.attributes.name}`)
  }
}
