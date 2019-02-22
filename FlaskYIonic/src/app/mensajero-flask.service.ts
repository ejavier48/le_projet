import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { HttpClient } from '@angular/common/http';



@Injectable({
  providedIn: 'root'
})
export class MensajeroFlaskService {
static  ipAdd:string;
static  puerto:string;

  constructor( private http2: HttpClient) {


  }

getData(ipAdd:string, port:string):Observable<any>{


    let response1 = this.http2.get('http://'+ipAdd+':'+port+'/');
    console.log(JSON.stringify(response1.source.source.source));
    //console.log("respuesta "+JSON.stringify(response1.source.source.source.value.body));
    return (response1);
}



}
