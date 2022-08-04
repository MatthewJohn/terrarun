import { TestBed } from '@angular/core/testing';

import { OrganisationExistsGuard } from './organisation-exists.guard';

describe('OrganisationExistsGuard', () => {
  let guard: OrganisationExistsGuard;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    guard = TestBed.inject(OrganisationExistsGuard);
  });

  it('should be created', () => {
    expect(guard).toBeTruthy();
  });
});
