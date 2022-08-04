import { HttpClientTestingModule } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';

import { OrganisationExistsGuard } from './organisation-exists.guard';

describe('OrganisationExistsGuard', () => {
  let guard: OrganisationExistsGuard;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [ HttpClientTestingModule, RouterTestingModule ]
    });
    guard = TestBed.inject(OrganisationExistsGuard);
  });

  it('should be created', () => {
    expect(guard).toBeTruthy();
  });
});
