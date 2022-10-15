import { TestBed } from '@angular/core/testing';

import { ProjectExistsGuard } from './project-exists.guard';

describe('ProjectExistsGuard', () => {
  let guard: ProjectExistsGuard;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    guard = TestBed.inject(ProjectExistsGuard);
  });

  it('should be created', () => {
    expect(guard).toBeTruthy();
  });
});
