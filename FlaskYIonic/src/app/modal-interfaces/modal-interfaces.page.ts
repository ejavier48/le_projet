import { Component, OnInit } from '@angular/core';
//para controlar el Modal
import { ModalController } from '@ionic/angular';
@Component({
  selector: 'app-modal-interfaces',
  templateUrl: './modal-interfaces.page.html',
  styleUrls: ['./modal-interfaces.page.scss'],
})
export class ModalInterfacesPage implements OnInit {

  imagen : string = '';
  imagenes :string[] = ['', 'https://i.ytimg.com/vi/kV4vHpqrj6E/hqdefault.jpg'];
  index : number = 0;
  value;
  name;
  interface;
  tiempo;
  constructor(private modalc:ModalController) {
    this.tiempo=this.getFormattedDate();

    let intervalHandle = setInterval(()=> {
      this.imagen = this.imagenes[this.index];
      this.index++;

      if(this.index == this.imagenes.length)
      {
        this.index=0;

      }

      this.tiempo=this.getFormattedDate();

    },2000);

   }


  getFormattedDate() {
    var date = new Date();
    var str = date.getFullYear() + "-" + (date.getMonth() + 1) + "-" + date.getDate() + " " +  date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds();

    return str;
}
  ngOnInit() {

    console.log(`${this.value}`);
    console.log(`${this.interface}`);

    this.imagen="http://192.168.0.25:8080/images/"+this.name+"/interface"+this.value;
    this.imagenes[0]=this.imagen;
  }

  cerrarModal(){
      this.modalc.dismiss();
  }

}
