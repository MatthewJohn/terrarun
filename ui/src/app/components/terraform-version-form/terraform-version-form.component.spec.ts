import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TerraformVersionFormComponent } from './terraform-version-form.component';

describe('TerraformVersionFormComponent', () => {
  let component: TerraformVersionFormComponent;
  let fixture: ComponentFixture<TerraformVersionFormComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TerraformVersionFormComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TerraformVersionFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
