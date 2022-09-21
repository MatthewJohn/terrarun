import { TaskResultService } from "src/app/task-result.service";

export class TaskResult {

    _id: string;
    _details: Promise<any> | undefined;
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

    async getColor(): Promise<string> {
        if (this._color === undefined) {
            let details = await this.getDetails();
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
        }
        return this._color;
    }

    async getTitle(): Promise<string> {
        if (this._title === undefined) {
            let details = await this.getDetails();
            this._title = details.data.id;
        }
        return this._title || '';
    }

    async getMessage(): Promise<string> {
        if (this._message === undefined) {
            let details = await this.getDetails();
            this._message = details.data.attributes.message;
        }
        return this._message || '';
    }

    getDetails(refreshDetails: boolean=false): Promise<any> {
        // Return details for task stage, caching in object
        if (this._details === undefined || refreshDetails) {
            this._details = this.taskResultService.getTaskResultDetailsById(this._id);
        }
        return this._details
    }
}
