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
intervalo
index
host
tiempo
imagen : string = '';
imagenes :string[] = ['', ''];
constructor(private router: Router, private activatedRoute: ActivatedRoute, private FlaskService: MensajeroFlaskService){
  this.indice = this.activatedRoute.snapshot.paramMap.get('indice');
  this.nombre = "";
  this.fecha = "";
  this.mostrarMensajeError = false;
  this.tiempo=this.getFormattedDate();

  this.intervalo = setInterval(()=> {
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
  volver(){

      this.router.navigate(['/ver-agente',this.indice]);
  }
  ngOnInit() {
    console.log(`${this.host}`);
    this.imagen="http://"+this.FlaskService.ipAdd+":"+this.FlaskService.puerto+"/images/rdd/predic"
    this.imagenes[0]=this.imagen;
    this.imagenes[1]=this.imagen;

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
