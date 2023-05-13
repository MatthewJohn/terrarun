import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TerraformVersionSelectComponent } from './terraform-version-select.component';

describe('TerraformVersionSelectComponent', () => {
  let component: TerraformVersionSelectComponent;
  let fixture: ComponentFixture<TerraformVersionSelectComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TerraformVersionSelectComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TerraformVersionSelectComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
