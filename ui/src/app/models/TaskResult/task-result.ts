import { map, Observable } from "rxjs";
import { TaskResultService } from "src/app/task-result.service";

export class TaskResult {

    _id: string;
    details$: Observable<any>;
    color: string;
    message: string;
    name: string;

    constructor(id: string,
            private taskResultService: TaskResultService) {
        this._id = id;
        this.color = 'basic';
        this.message = '';
        this.name = '';

        this.details$ = this.taskResultService.getTaskResultDetailsById(this._id);
        this.details$.subscribe((details) => {
            let status = details.data.attributes.status;
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

            this.message = details.data.attributes.message;
            this.name = details.data.id;
        });
    }
}
