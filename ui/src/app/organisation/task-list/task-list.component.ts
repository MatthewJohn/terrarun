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

  editTask: any = null;

  nameValidStates = {
    invalid: {icon: 'close-outline', valid: false, iconStatus: 'danger'},
    valid: {icon: 'checkmark-circle-outline', valid: true, iconStatus: 'success'},
    loading: {icon: 'loader-outline', valid: false, iconStatus: 'info'}
  };

  createTaskNameValid: {icon: string, valid: boolean, iconStatus: string} = this.nameValidStates.invalid;
  createForm = this.formBuilder.group({
    name: '',
    description: '',
    url: '',
    hmacKey: ''
  });

  editTaskNameValid: {icon: string, valid: boolean, iconStatus: string} = this.nameValidStates.invalid;
  editForm = this.formBuilder.group({
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

  validateNewTaskName(): void {
    this.createTaskNameValid = this.nameValidStates.loading;

    this.taskService.validateNewTaskName(this.organisationName || '', this.createForm.value.name).then((validationResult) => {
      this.createTaskNameValid = validationResult.data.valid ? this.nameValidStates.valid : this.nameValidStates.invalid;
    });
  }
  onCreate(): void {
    this.taskService.create(this.organisationName || '',
                            this.createForm.value.name,
                            this.createForm.value.description,
                            this.createForm.value.url,
                            this.createForm.value.hmacKey,
                            true
                            ).then((task) => {
      // Refresh task list
      this.getTaskList();

      // Reset create form
      this.editForm.setValue({
        name: '',
        description: '',
        url: '',
        hmacKey: ''
      })
    });
  }

  validateEditTaskName(): void {

    this.editTaskNameValid = this.nameValidStates.loading;

    // If name matches original value, set as valid
    if (this.editForm.value.name == this.editTask.attributes.name) {
      this.editTaskNameValid = this.nameValidStates.valid;
      return;
    }

    this.taskService.validateNewTaskName(this.organisationName || '', this.editForm.value.name).then((validationResult) => {
      this.editTaskNameValid = validationResult.data.valid ? this.nameValidStates.valid : this.nameValidStates.invalid;
    });
  }

  onTaskClick(target: any) {
    // Setup edit form for task
    this.editTask = target.data;
    console.log(target.data);
    this.editForm.setValue({
      name: this.editTask.attributes.name,
      description: this.editTask.attributes.description,
      url: this.editTask.attributes.url,
      hmacKey: this.editTask.attributes['hmac-key']
    });
    this.editTaskNameValid = this.nameValidStates.valid;
  }
  cancelEdit() {
    this.editTask = null;
  }
  onEdit() {
    this.taskService.updateAttributes(
      this.editTask.id,
      this.editForm.value.name,
      this.editForm.value.description,
      this.editForm.value.url,
      this.editForm.value.hmacKey,
      true
    ).then(() => {
      this.editTask = null;
      this.getTaskList();
    });
  }
}
