import { Component, OnInit } from '@angular/core';
import { FormBuilder } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { map, Observable, switchMap } from 'rxjs';
import { OrganisationService } from 'src/app/organisation.service';
import { OrganisationStateType, StateService } from 'src/app/state.service';
import { TaskService } from 'src/app/task.service';

@Component({
  selector: 'app-task-list',
  templateUrl: './task-list.component.html',
  styleUrls: ['./task-list.component.scss']
})
export class TaskListComponent implements OnInit {
  tasks$: Observable<any>;
  tableColumns: string[] = ['name', 'description', 'enabled'];
  organisationName: string | null = null;

  nameValidStates = {
    invalid: {icon: 'close-outline', valid: false, iconStatus: 'danger'},
    valid: {icon: 'checkmark-circle-outline', valid: true, iconStatus: 'success'},
    loading: {icon: 'loader-outline', valid: false, iconStatus: 'info'}
  };
  nameValid: {icon: string, valid: boolean, iconStatus: string} = this.nameValidStates.invalid;
  form = this.formBuilder.group({
    name: '',
    description: '',
    url: '',
    hmacKey: ''
  });

  currentOrganisation: OrganisationStateType | null = null;

  constructor(private state: StateService,
              private taskService: TaskService,
              private router: Router,
              private route: ActivatedRoute,
              private formBuilder: FormBuilder) {
    this.tasks$ = new Observable();
    this.route.paramMap.subscribe(params => {
        this.organisationName = params.get('organisationName');
        this.getTaskList();
    });

    this.state.currentOrganisation.subscribe((data) => this.currentOrganisation = data);
  }

  getTaskList(): void {
    this.tasks$ = this.taskService.getTasksByOrganisation(this.organisationName || "").pipe(
      map((data) => {
        return Array.from({length: data.data.length},
          (_, n) => ({'data': data.data[n]}))
      })
    );
  }

  ngOnInit(): void {

  }

  validateName(): void {
    this.nameValid = this.nameValidStates.loading;

    this.taskService.validateNewTaskName(this.organisationName || '', this.form.value.name).then((validationResult) => {
      this.nameValid = validationResult.data.valid ? this.nameValidStates.valid : this.nameValidStates.invalid;
    });
  }
  onCreate(): void {
    this.taskService.create(this.organisationName || '',
                            this.form.value.name,
                            this.form.value.description,
                            this.form.value.url,
                            this.form.value.hmacKey,
                            true
                            ).then((task) => {
      // Refresh task list
      this.getTaskList();
    });
  }

  onTaskClick(target: any) {
    // Do nothing
    console.log(target.data);
    //this.router.navigateByUrl(`/${this.organisationName}/${target.data.attributes.name}`)
  }
}
