import { TestBed } from '@angular/core/testing';

import { LifecycleEnvironmentGroupService } from './lifecycle-environment-group.service';

describe('LifecycleEnvironmentGroupService', () => {
  let service: LifecycleEnvironmentGroupService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(LifecycleEnvironmentGroupService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
