import { TestBed } from '@angular/core/testing';

import { LifecycleExistsGuard } from './lifecycle-exists.guard';

describe('LifecycleExistsGuard', () => {
  let guard: LifecycleExistsGuard;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    guard = TestBed.inject(LifecycleExistsGuard);
  });

  it('should be created', () => {
    expect(guard).toBeTruthy();
  });
});
