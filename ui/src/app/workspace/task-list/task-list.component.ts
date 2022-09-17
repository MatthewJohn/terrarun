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
  workspaceTasks$: Observable<any>;
  organisationTasks$: Observable<any>;
  tableColumns: string[] = ['Name', '', 'enabled'];

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
    this.workspaceTasks$ = new Observable();
    this.organisationTasks$ = new Observable();

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
    this.organisationTasks$ = this.taskService.getTasksByOrganisation(this.currentOrganisation?.id || "").pipe();
  }

  getWorkspaceTaskList(): void {
    this.workspaceTasks$ = this.workspaceTaskService.getWorkspaceTasksByWorkspace(this.currentWorkspace?.id || "");
  }

  ngOnInit(): void {

  }

  onAssociate(): void {
    // this.workspaceTaskService.associateTask(this.workspaceId || '',
    //                                         this.associateForm.value.taskId,
    //                                         this.associateForm.value.stage,
    //                                         this.associateForm.value.enforcementLevel
    //                                        ).then((task) => {
    //   // Refresh task list
    //   this.getWorkspaceTaskList();

    //   // Reset create form
    //   this.associateForm.setValue({
    //     taskId: null,
    //     stage: '',
    //     enforcementLevel: ''
    //   })
    // });
  }
}