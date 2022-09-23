import { TestBed } from '@angular/core/testing';

import { WorkspaceTaskService } from './workspace-task.service';

describe('WorkspaceTaskService', () => {
  let service: WorkspaceTaskService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(WorkspaceTaskService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
