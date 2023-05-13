import { TestBed } from '@angular/core/testing';

import { TerraformVersionService } from './terraform-version.service';

describe('TerraformVersionService', () => {
  let service: TerraformVersionService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(TerraformVersionService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
