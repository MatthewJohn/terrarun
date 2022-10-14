import { TestBed } from '@angular/core/testing';

import { MetaWorkspaceExistsGuard } from './meta-workspace-exists.guard';

describe('MetaWorkspaceExistsGuard', () => {
  let guard: MetaWorkspaceExistsGuard;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    guard = TestBed.inject(MetaWorkspaceExistsGuard);
  });

  it('should be created', () => {
    expect(guard).toBeTruthy();
  });
});
