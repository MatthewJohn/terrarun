import { map, Observable } from "rxjs";
import { TaskResultService } from "src/app/task-result.service";
import { TaskStageService } from "src/app/task-stage.service";
import { TaskResult } from "../TaskResult/task-result";

export class TaskStage {
    _id: string;
    details$: Observable<any>;
    taskResults: TaskResult[];
    color: string;

    constructor(id: string,
            private taskStageService: TaskStageService,
            private taskResultService: TaskResultService) {
        this._id = id;
        this.details$ = this.taskStageService.getTaskStageDetailsById(this._id);

        this.taskResults = [];
        this.color = 'basic';
        this.details$.subscribe((data) => {
            let status = data.data.attributes.status;
            if (status == 'pending') {
                this.color = 'info';
            } else if (status == 'running') {
                this.color = 'info';
            } else if (status == 'passed') {
                this.color = 'success'
            } else if (status == 'failed') {
                this.color = 'danger';
            } else if (status == 'errored') {
                this.color = 'danger';
            } else if (status == 'canceled') {
                this.color = 'danger';
            }

            let taskResults = [];
            for (let taskResultData of data.data.relationships['task-results'].data) {
                taskResults.push(new TaskResult(taskResultData.id, this.taskResultService));
            }
            this.taskResults = taskResults;
        })
    }
}
