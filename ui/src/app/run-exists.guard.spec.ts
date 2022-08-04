import { TestBed } from '@angular/core/testing';

import { RunExistsGuard } from './run-exists.guard';

describe('RunExistsGuard', () => {
  let guard: RunExistsGuard;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    guard = TestBed.inject(RunExistsGuard);
  });

  it('should be created', () => {
    expect(guard).toBeTruthy();
  });
});
