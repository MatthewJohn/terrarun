import { Component, OnInit } from '@angular/core';
import { FormBuilder } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { map, Observable } from 'rxjs';
import { OrganisationStateType, StateService, WorkspaceStateType } from 'src/app/state.service';
import { TaskService } from 'src/app/task.service';
import { WorkspaceTaskService } from 'src/app/workspace-task.service';

@Component({
  selector: 'app-task-list',
  templateUrl: './task-list.component.html',
  styleUrls: ['./task-list.component.scss']
})
export class TaskListComponent implements OnInit {
  // All tasks associated with workspace
  workspaceTasks: any[];
  // All tasks available in organisation
  organisationTasks: any[];
  // Map of task details by task Id
  tasksById: any;
  tableColumns: string[] = ['Name', 'Enforcement', 'Stage', 'Delete'];

  associateForm = this.formBuilder.group({
    taskId: '',
    stage: '',
    enforcementLevel: ''
  });

  currentOrganisation: OrganisationStateType | null = null;
  currentWorkspace: WorkspaceStateType | null = null;

  constructor(private state: StateService,
              private workspaceTaskService: WorkspaceTaskService,
              private taskService: TaskService,
              private router: Router,
              private route: ActivatedRoute,
              private formBuilder: FormBuilder) {
                
    this.workspaceTasks = [];
    this.organisationTasks = [];
    this.tasksById = {};

    this.state.currentOrganisation.subscribe((data) => {
      this.currentOrganisation = data;
      if (this.currentOrganisation.id != null)
        this.getOrganisationTasks();
    });
    this.state.currentWorkspace.subscribe((data) => {
      this.currentWorkspace = data;

      if (this.currentWorkspace.name != null)
        this.getWorkspaceTaskList();
    });
  }

  getOrganisationTasks(): void {
    this.taskService.getTasksByOrganisation(this.currentOrganisation?.id || "").subscribe((data) => {
      this.organisationTasks = data.data;
      this.organisationTasks.forEach((taskDetails) => {
        this.tasksById[taskDetails.id] = taskDetails;
      });
    });
  }

  getWorkspaceTaskList(): void {
    this.workspaceTaskService.getWorkspaceTasksByWorkspace(
      this.currentWorkspace?.id || "").subscribe((data) => {
        this.workspaceTasks = data.data;
      });
  }

  ngOnInit(): void {

  }

  onAssociate(): void {
    this.workspaceTaskService.associateTask(this.currentWorkspace?.id || '',
                                            this.associateForm.value.taskId,
                                            this.associateForm.value.stage,
                                            this.associateForm.value.enforcementLevel
                                           ).then((task) => {
      // Refresh task list
      this.getWorkspaceTaskList();

      // Reset create form
      this.associateForm.setValue({
        taskId: null,
        stage: '',
        enforcementLevel: ''
      })
    });
  }

  deleteWorkspaceTask(workspaceTaskId: string): void {
    this.workspaceTaskService.delete(this.currentWorkspace?.id || "", workspaceTaskId).then(() => {
      this.getWorkspaceTaskList();
    });
  }
}