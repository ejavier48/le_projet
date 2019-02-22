import { CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AddAgentPage } from './add-agent.page';

describe('AddAgentPage', () => {
  let component: AddAgentPage;
  let fixture: ComponentFixture<AddAgentPage>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AddAgentPage ],
      schemas: [CUSTOM_ELEMENTS_SCHEMA],
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AddAgentPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
