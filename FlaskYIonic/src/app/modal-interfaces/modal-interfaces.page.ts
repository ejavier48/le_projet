import { Component, OnInit } from '@angular/core';
//para controlar el Modal
import { ModalController } from '@ionic/angular';
//importo el servicio para conectarme a flask
import { MensajeroFlaskService } from '../mensajero-flask.service';

@Component({
  selector: 'app-modal-interfaces',
  templateUrl: './modal-interfaces.page.html',
  styleUrls: ['./modal-interfaces.page.scss'],
})
export class ModalInterfacesPage implements OnInit {

  imagen : string = '';
  imagenes :string[] = ['', ''];
  index : number = 0;
  value;
  name;
  interface;
  tiempo;
  ipAdd:string;
  puerto:string;
  constructor(private modalc:ModalController, private FlaskService: MensajeroFlaskService) {
    this.ipAdd=this.FlaskService.ipAdd;
    this.puerto=this.FlaskService.puerto;

    this.tiempo=this.getFormattedDate();

    let intervalHandle = setInterval(()=> {
      this.imagen = this.imagenes[this.index];
      this.agregaTimeStamp();
      this.index++;

      if(this.index == this.imagenes.length)
      {
        this.index=0;

      }

      this.tiempo=this.getFormattedDate();

    },2000);

   }


   agregaTimeStamp(){
     this.imagen+="?"+  Math.random().toString(36).substr(2, 9);

     console.log(this.imagen);
   }

  getFormattedDate() {
    var date = new Date();
    var str = date.getFullYear() + "-" + (date.getMonth() + 1) + "-" + date.getDate() + " " +  date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds();

    return str;
}
  ngOnInit() {

    console.log(`${this.value}`);
    console.log(`${this.interface}`);

    this.imagen="http://"+this.ipAdd+":"+this.puerto+"/images/"+this.name+"/interface"+this.value;
    this.imagenes[0]=this.imagen;
    this.imagenes[1]=this.imagen;

  }

  cerrarModal(){
      this.modalc.dismiss();
  }

}
