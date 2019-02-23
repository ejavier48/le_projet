import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
//para hacer peticiones
import { HttpClient } from '@angular/common/http';
//para mandar alertas
import { AlertController } from '@ionic/angular';
//para mostrar el loading
import { LoadingController } from '@ionic/angular';
//para poder moverme entre pantallas
import { Router } from "@angular/router";




@Injectable({
  providedIn: 'root'
})
export class MensajeroFlaskService {
  ipAdd:string;
  puerto:string;
  agenteConsultado:any;
  constructor( private http2: HttpClient, private alertC: AlertController,private loadcont: LoadingController,private router: Router) {


  }

getData(ipAdd:string, port:string):Observable<any>{
    this.ipAdd=ipAdd;
    this.puerto=port;
    let response1 = this.http2.get('http://'+ipAdd+':'+port+'/');
    console.log(JSON.stringify(response1.source.source.source));
    //console.log("respuesta "+JSON.stringify(response1.source.source.source.value.body));
    return (response1);
}

async addAgent(ipAdd:string, comunidad:string, version:string, puerto:string){
  const loading = await this.loadcont.create({
    message: 'Agregando'
  });
  await loading.present();

  let postData = {
            "host": ipAdd,
            "version": version,
            "port": puerto,
            "community": comunidad
    }

  this.http2.post('http://'+this.ipAdd+':'+this.puerto+'/add',postData).subscribe(res => {
          console.log(res);
          loading.dismiss();
          if(JSON.stringify(res).includes("error")){
            this.presentAlert("Oops!","Parece que hubo un error al agregar el agente :c");
              this.deleteAgent(ipAdd,0);
          }
          else{
            this.presentAlert("Perfecto!","Agente dado de alta con exito");
          }

        },
        err => {
          console.log("Error occured "+err);
          loading.dismiss();
          this.presentAlert("Oops!",err);
        });


}

async deleteAgent(ipAdd:string, bandera:number) {
  console.log("entre a delete");
  this.http2.post('http://'+this.ipAdd+':'+this.puerto+'/delete',{"host":ipAdd}).subscribe(res=>{
    console.log("elimino el error")
    if(bandera==1){
        this.presentAlert("Agente eliminado","Se elimino el agente con exito");
    }

  }, err=>{
    console.log("error al eliminar "+err)
    if(bandera==1)
      this.presentAlert("Oops!","No pude eliminar al agente");
  })
}

async presentAlert(titulo:string,mensaje:string) {
   const alert = await this.alertC.create({
     header: titulo,
     message: mensaje,
     buttons: [{
       text:'OK',
       handler: () => {
           console.log('Confirm Okay');
           this.router.navigate(['/menu',this.ipAdd, this.puerto,'menu','menu','consulta',this.ipAdd, this.puerto]);
         }
     }]
   });

   await alert.present();
 }



}
