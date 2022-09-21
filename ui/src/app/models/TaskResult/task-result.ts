import { Observable } from "rxjs";
import { TaskResultService } from "src/app/task-result.service";

export class TaskResult {

    _id: string;
    _details: Observable<any> | null;
    _color: string | null;

    constructor(id: string,
            private taskResultService: TaskResultService) {
        this._id = id;
        this._details = null;
        this._color = null;
    }
}
