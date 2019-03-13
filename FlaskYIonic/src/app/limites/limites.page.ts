import { Component, OnInit } from '@angular/core';
//para poder moverme entre pantallas
import { Router } from "@angular/router";
//para recibir parametros
import { ActivatedRoute } from "@angular/router";
//importo el servicio para conectarme a flask
import { MensajeroFlaskService } from '../mensajero-flask.service';

@Component({
  selector: 'app-limites',
  templateUrl: './limites.page.html',
  styleUrls: ['./limites.page.scss'],
})
export class LimitesPage implements OnInit {

  mostrarMensajeError;
  indice;
  esConsulta;
  intervalo;
  limites=[];
  RAM = [];
  CPU = [];
  HDD = [];
  constructor(private router: Router, private activatedRoute: ActivatedRoute, private FlaskService: MensajeroFlaskService){
      this.indice = this.activatedRoute.snapshot.paramMap.get('indice');
      this.esConsulta = this.activatedRoute.snapshot.paramMap.get('esConsulta');
      this.mostrarMensajeError = false
      if(this.esConsulta){
          this.getData()

      }
      else{
        for (let i = 0; i < 3; i++) {
            this.RAM[i]="";
            this.CPU[i]="";
            this.HDD[i]="";
        }
      }

  }

  volver(){

      this.router.navigate(['/ver-agente',this.indice]);
  }
  ngOnInit() {

  }

  guardarLims(){
    let bandera = true;

    for (let i = 0; i < 3; i++) {
        if(this.RAM[i]=="" || this.CPU[i]=="" || this.HDD[i]==""){
          bandera=false
          break;
        }

    }

    if(bandera){
      this.mostrarMensajeError=false;
      this.FlaskService.setLimits(this.RAM, this.CPU, this.HDD);
    
    }
    else{
      this.mostrarMensajeError=true;
    }
  }


  async getData(){
    let data;

    this.FlaskService.getLimits()
      .subscribe(res => {
        this.limites.push(res.CPU);
        this.limites.push(res.RAM);
        this.limites.push(res.HDD);
        console.log(this.limites);
        this.CPU[0]=this.limites[0].Ready;
        this.CPU[1]=this.limites[0].Set;
        this.CPU[2]=this.limites[0].Go;

        this.RAM[0]=this.limites[1].Ready;
        this.RAM[1]=this.limites[1].Set;
        this.RAM[2]=this.limites[1].Go;

        this.HDD[0]=this.limites[2].Ready;
        this.HDD[1]=this.limites[2].Set;
        this.HDD[2]=this.limites[2].Go;
          //console.log("data obtenida "+JSON.stringify(res));
      },err => {
        console.log("error:"+JSON.stringify(err));
        //this.router.navigate(['/']);

        //  this.presentAlert(JSON.stringify(err));

      });
  }

}
