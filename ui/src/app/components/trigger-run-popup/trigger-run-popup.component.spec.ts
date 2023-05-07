import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TriggerRunPopupComponent } from './trigger-run-popup.component';

describe('TriggerRunPopupComponent', () => {
  let component: TriggerRunPopupComponent;
  let fixture: ComponentFixture<TriggerRunPopupComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TriggerRunPopupComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TriggerRunPopupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
