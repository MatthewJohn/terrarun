import { TestBed } from '@angular/core/testing';

import { EnvironmentLifecycleService } from './environment-lifecycle.service';

describe('EnvironmentLifecycleService', () => {
  let service: EnvironmentLifecycleService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(EnvironmentLifecycleService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
