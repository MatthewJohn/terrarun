import { TestBed } from '@angular/core/testing';

import { LifecycleEnvironmentService } from './lifecycle-environment.service';

describe('LifecycleEnvironmentService', () => {
  let service: LifecycleEnvironmentService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(LifecycleEnvironmentService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
