import { CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { LimitesPage } from './limites.page';

describe('LimitesPage', () => {
  let component: LimitesPage;
  let fixture: ComponentFixture<LimitesPage>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ LimitesPage ],
      schemas: [CUSTOM_ELEMENTS_SCHEMA],
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(LimitesPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
