import { TestBed } from '@angular/core/testing';

import { MensajeroFlaskService } from './mensajero-flask.service';

describe('MensajeroFlaskService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: MensajeroFlaskService = TestBed.get(MensajeroFlaskService);
    expect(service).toBeTruthy();
  });
});
