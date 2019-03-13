import { CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PrediccionPage } from './prediccion.page';

describe('PrediccionPage', () => {
  let component: PrediccionPage;
  let fixture: ComponentFixture<PrediccionPage>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PrediccionPage ],
      schemas: [CUSTOM_ELEMENTS_SCHEMA],
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PrediccionPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
