import { Component, OnInit } from '@angular/core';

//importo el servicio para conectarme a flask
import { MensajeroFlaskService } from '../mensajero-flask.service';

@Component({
  selector: 'app-administrador',
  templateUrl: './administrador.page.html',
  styleUrls: ['./administrador.page.scss'],
})
export class AdministradorPage implements OnInit {
  Vista:string;
  email:string;
  nombre: string;
  tel: string;
  verMensajeError: boolean;

  constructor(private FlaskService: MensajeroFlaskService) {
    this.email="";
    this.tel="";
    this.nombre="";

    this.verMensajeError = false;
    if(this.FlaskService.hayInfoAdmin){
      this.Vista="ver";
      this.email = this.FlaskService.infoAdmin.email;
      this.tel = this.FlaskService.infoAdmin.tel;
      this.nombre = this.FlaskService.infoAdmin.nombre;
    }
    else{
      this.Vista="editar"
    }
   }

  ngOnInit() {
  }



  guardarAdmin(){
    if(this.email=="" && this.nombre=="" && this.tel=="")
        this.verMensajeError = true;
    else{
      this.verMensajeError = false;
      this.FlaskService.guardar_storage(this.nombre, this.tel, this.email);
    }
  }

}
