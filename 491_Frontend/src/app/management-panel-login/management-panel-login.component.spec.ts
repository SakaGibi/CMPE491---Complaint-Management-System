import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ManagementPanelLoginComponent } from './management-panel-login.component';

describe('ManagementPanelLoginComponent', () => {
  let component: ManagementPanelLoginComponent;
  let fixture: ComponentFixture<ManagementPanelLoginComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ManagementPanelLoginComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ManagementPanelLoginComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
