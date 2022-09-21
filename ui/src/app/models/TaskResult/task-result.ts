import { map, Observable } from "rxjs";
import { TaskResultService } from "src/app/task-result.service";

export class TaskResult {

    _id: string;
    _details: Observable<any> | undefined;
    _color: string | undefined;
    _message: string | undefined;
    _title: string | undefined;

    constructor(id: string,
            private taskResultService: TaskResultService) {
        this._id = id;
        this._details = undefined;
        this._color = undefined;
        this._message = undefined;
        this._title = undefined;
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

    getTitle(): Observable<string> {
        return this.getDetails().pipe(map((details) => {
            return details.data.id;
        }));
    }

    getMessage(): Observable<string> {
        return this.getDetails().pipe(map((details) => {
            return details.data.attributes.message;
        }));
    }

    getDetails(refreshDetails: boolean=false): Observable<any> {
        // Return details for task stage, caching in object
        if (this._details === undefined || refreshDetails) {
            this._details = this.taskResultService.getTaskResultDetailsById(this._id);
        }
        return this._details
    }
}
