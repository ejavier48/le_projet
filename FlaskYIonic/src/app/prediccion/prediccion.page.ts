import { Component, OnInit } from '@angular/core';
//para poder moverme entre pantallas
import { Router } from "@angular/router";
//para recibir parametros
import { ActivatedRoute } from "@angular/router";
//importo el servicio para conectarme a flask
import { MensajeroFlaskService } from '../mensajero-flask.service';
@Component({
  selector: 'app-prediccion',
  templateUrl: './prediccion.page.html',
  styleUrls: ['./prediccion.page.scss'],
})
export class PrediccionPage implements OnInit {
indice
fecha
nombre
mostrarMensajeError
mostrarImagen
constructor(private router: Router, private activatedRoute: ActivatedRoute, private FlaskService: MensajeroFlaskService){
  this.indice = this.activatedRoute.snapshot.paramMap.get('indice');
  this.nombre = "";
  this.fecha = "";
  this.mostrarMensajeError = false;

 }

  volver(){

      this.router.navigate(['/ver-agente',this.indice]);
  }
  ngOnInit() {

  }



  generarGrafica(){
    if(this.nombre=="" || this.fecha==""){
      this.mostrarMensajeError=true;
    }
    else{
      this.mostrarMensajeError=false;
       var newStr = this.fecha.replace(/T/g, " ").replace(/Z/g,"");
      console.log(newStr)
      this.FlaskService.generatePrediction(this.nombre, newStr, this.indice)
      this.mostrarImagen =  true


    }

  }

}
