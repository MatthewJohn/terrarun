import { TestBed } from '@angular/core/testing';

import { SiteAdminGuard } from './site-admin.guard';

describe('SiteAdminGuard', () => {
  let guard: SiteAdminGuard;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    guard = TestBed.inject(SiteAdminGuard);
  });

  it('should be created', () => {
    expect(guard).toBeTruthy();
  });
});
