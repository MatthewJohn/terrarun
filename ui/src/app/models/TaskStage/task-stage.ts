import { map, Observable } from "rxjs";
import { TaskResultService } from "src/app/task-result.service";
import { TaskStageService } from "src/app/task-stage.service";
import { TaskResult } from "../TaskResult/task-result";

export class TaskStage {
    _id: string;
    _details: Observable<any> | undefined;
    _color: string | null;
    _taskResults: Observable<any> | undefined;

    constructor(id: string,
            private taskStageService: TaskStageService,
            private taskResultService: TaskResultService) {
        this._id = id;
        this._details = undefined;
        this._color = null;
        this._taskResults = undefined;
    }

    getTaskResults(): Observable<any> {
        if (this._taskResults === undefined) {
            this._taskResults = this.getDetails().pipe(map((data) => {
                let taskResults = [];
                for (let taskResultData of data.data.relationships['task-results'].data) {
                    taskResults.push(new TaskResult(taskResultData.id, this.taskResultService));
                }
                return taskResults;
            }));
        }
        return this._taskResults;
    }

    getColor(): Observable<string> {
        return this.getDetails().pipe(map((details) => {
            let status = details.data.attributes.status;
            let color = 'basic';
            if (status == 'pending') {
                color = 'info';
            } else if (status == 'running') {
                color = 'info';
            } else if (status == 'passed') {
                color = 'success'
            } else if (status == 'failed') {
                color = 'danger';
            } else if (status == 'errored') {
                color = 'danger';
            } else if (status == 'canceled') {
                color = 'danger';
            }
            return color;
        }));
    }

    getDetails(refreshDetails: boolean=false): Observable<any> {
        // Return details for task stage, caching in object
        if (this._details === undefined || refreshDetails) {
            this._details = this.taskStageService.getTaskStageDetailsById(this._id);
        }
        return this._details
    }
}
