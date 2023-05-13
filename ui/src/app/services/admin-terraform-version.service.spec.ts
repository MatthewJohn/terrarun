import { TestBed } from '@angular/core/testing';

import { AdminTerraformVersionService } from './admin-terraform-version.service';

describe('AdminTerraformVersionsService', () => {
  let service: AdminTerraformVersionService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(AdminTerraformVersionService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
