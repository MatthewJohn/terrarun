import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TerraformVersionsComponent } from './terraform-versions.component';

describe('TerraformVersionsComponent', () => {
  let component: TerraformVersionsComponent;
  let fixture: ComponentFixture<TerraformVersionsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TerraformVersionsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TerraformVersionsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
