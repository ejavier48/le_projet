import { Component, OnInit } from '@angular/core';
//importo el servicio para conectarme a flask
import { MensajeroFlaskService } from '../mensajero-flask.service';

@Component({
  selector: 'app-add-agent',
  templateUrl: './add-agent.page.html',
  styleUrls: ['./add-agent.page.scss'],
})
export class AddAgentPage implements OnInit {

  ipAdd:string;
  comunidad:string;
  version:string;
  puerto:string;
  showAlert:boolean;

  constructor(private mensajeFlask: MensajeroFlaskService) {
    this.ipAdd="";
    this.comunidad="";
    this.version="";
    this.puerto="";
    this.showAlert=false;
  }

  ngOnInit() {
  }

  agregarAgente(){
    if(this.ipAdd=="" || this.comunidad=="" ||this.version=="" || this.puerto==""){
      this.showAlert = true;

    }
    else{
      this.mensajeFlask.addAgent(this.ipAdd,this.comunidad, this.version, this.puerto);
      this.showAlert = false ;

    }


  }

}
