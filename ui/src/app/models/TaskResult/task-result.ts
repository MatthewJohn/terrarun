import { TaskResultService } from "src/app/task-result.service";

export class TaskResult {

    _id: string;
    _details: Promise<any> | undefined;
    _color: string | undefined;

    constructor(id: string,
            private taskResultService: TaskResultService) {
        this._id = id;
        this._details = undefined;
        this._color = undefined;
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
            this._details = this.taskResultService.getTaskResultDetailsById(this._id);
        }
        return this._details
    }
}
