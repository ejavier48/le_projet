import { Injectable } from '@angular/core';
import { Observable, of, throwError, timer } from 'rxjs';

import { HttpClient, HttpHeaders, HttpErrorResponse } from '@angular/common/http';

import {
  timeout,
  retryWhen,
  take,
  concat,
  share,
  delayWhen
} from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class MensajeroFlaskService {

  constructor( private http2: HttpClient) {


  }

getData(ipAdd:string, port:string):Observable<any>{


    let response1 = this.http2.get('http://'+ipAdd+':'+port+'/');
    console.log(JSON.stringify(response1.source.source.source));
    //console.log("respuesta "+JSON.stringify(response1.source.source.source.value.body));
    return (response1);
}



}
