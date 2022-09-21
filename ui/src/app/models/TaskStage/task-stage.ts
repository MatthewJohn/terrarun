import { Observable } from "rxjs";
import { TaskResultService } from "src/app/task-result.service";
import { TaskStageService } from "src/app/task-stage.service";
import { TaskResult } from "../TaskResult/task-result";

export class TaskStage {
    _id: string;
    _details: Promise<any> | undefined;
    _color: string | null;
    _taskResults: Promise<any> | undefined;

    constructor(id: string,
            private taskStageService: TaskStageService,
            private taskResultService: TaskResultService) {
        this._id = id;
        this._details = undefined;
        this._color = null;
        this._taskResults = undefined;
    }

    getTaskResults(): any {
        if (this._taskResults === undefined) {
            this._taskResults = new Promise((resolve, reject) => {
                this.getDetails().then((data) => {
                    let taskResults = [];
                    for (let taskResultData of data.data.relationships['task-results'].data) {
                        taskResults.push(new TaskResult(taskResultData.id, this.taskResultService));
                    }
                    resolve(taskResults);
                });
            });
        }
        return this._taskResults;
    }

    getColor(): Promise<string> {
        return new Promise((resolve, reject) => {
            if (this._color == null) {
                this.getDetails().then((details) => {
                    if (details.data?.attributes?.status) {
                        let status = details.data.attributes.status;
                        if (status == 'pending') {
                            this._color = 'info';
                        } else if (status == 'running') {
                            this._color = 'info';
                        } else if (status == 'passed') {
                            this._color = 'success'
                        } else if (status == 'failed') {
                            this._color = 'danger';
                        } else if (status == 'errored') {
                            this._color = 'danger';
                        } else if (status == 'canceled') {
                            this._color = 'danger';
                        } else {
                            this._color = 'basic';
                        }
                        resolve(this._color);
                    }
                });
            } else {
                resolve(this._color);
            }
        });
    }

    getDetails(refreshDetails: boolean=false): Promise<any> {
        // Return details for task stage, caching in object
        if (this._details === undefined || refreshDetails) {
            this._details = this.taskStageService.getTaskStageDetailsById(this._id);
        }
        return this._details
    }
}
