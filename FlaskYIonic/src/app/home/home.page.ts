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
