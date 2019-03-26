import { Component } from '@angular/core';

//para poder moverme entre pantallas
import { Router } from "@angular/router";

//importo el servicio para conectarme a flask
import { MensajeroFlaskService } from '../mensajero-flask.service';

@Component({
  selector: 'app-home',
  templateUrl: 'home.page.html',
  styleUrls: ['home.page.scss'],
})
export class HomePage {
  ipAdd:string;
  port:string;
  showAlert: boolean;
  constructor(private router: Router, private FlaskService: MensajeroFlaskService){
    this.showAlert = false;
    this.ipAdd="";
    this.port="";
  }

  ionViewDidEnter(){
    this.FlaskService.pausarInteravalo1=true;
  }

/*  send(){
    console.log( "ready!" );
    alert("he");
    Email.send("zildjianremo@gmail.com",
    "zildjianremo@gmail.com",
    "SNMP Notificacion de cambio de estado",
    "texto",
    "smtp25.elasticemail.com",
    "zildjianremo@gmail.com",
    "cd26d587-db2c-48f2-9d9d-6da0cc766915",
    function done(message) {
      alert(message)
   });
 }*/



  irAConsulta(){
    if(this.ipAdd=="" || this.port==""){
      console.log(this.ipAdd);
      console.log(this.port);
      console.log("error");
      this.showAlert = true;



    }
    else{
        this.FlaskService.pausarInteravalo1=false;
      this.router.navigate(['/menu',this.ipAdd, this.port,'menu','menu','consulta',this.ipAdd, this.port]);
      this.showAlert = false ;

    }



  }



}
