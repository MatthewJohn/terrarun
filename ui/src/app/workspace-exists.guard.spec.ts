import { TestBed } from '@angular/core/testing';

import { WorkspaceExistsGuard } from './workspace-exists.guard';

describe('WorkspaceExistsGuard', () => {
  let guard: WorkspaceExistsGuard;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    guard = TestBed.inject(WorkspaceExistsGuard);
  });

  it('should be created', () => {
    expect(guard).toBeTruthy();
  });
});
