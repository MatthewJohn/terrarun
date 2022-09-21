import { TestBed } from '@angular/core/testing';

import { TaskResultService } from './task-result.service';

describe('TaskResultService', () => {
  let service: TaskResultService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(TaskResultService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
