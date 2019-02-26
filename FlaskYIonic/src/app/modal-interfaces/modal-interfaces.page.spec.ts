import { CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ModalInterfacesPage } from './modal-interfaces.page';

describe('ModalInterfacesPage', () => {
  let component: ModalInterfacesPage;
  let fixture: ComponentFixture<ModalInterfacesPage>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ModalInterfacesPage ],
      schemas: [CUSTOM_ELEMENTS_SCHEMA],
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ModalInterfacesPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
