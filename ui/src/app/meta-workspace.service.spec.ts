import { TestBed } from '@angular/core/testing';

import { MetaWorkspaceService } from './meta-workspace.service';

describe('MetaWorkspaceService', () => {
  let service: MetaWorkspaceService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(MetaWorkspaceService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
