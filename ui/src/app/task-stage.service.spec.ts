import { TestBed } from '@angular/core/testing';

import { TaskStageService } from './task-stage.service';

describe('TaskStageService', () => {
  let service: TaskStageService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(TaskStageService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
