import { CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { VerAgentePage } from './ver-agente.page';

describe('VerAgentePage', () => {
  let component: VerAgentePage;
  let fixture: ComponentFixture<VerAgentePage>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ VerAgentePage ],
      schemas: [CUSTOM_ELEMENTS_SCHEMA],
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(VerAgentePage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
